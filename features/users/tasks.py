import os

import db.connection
import configuration
import khLogging
import features.users.operations
from sqlalchemy.orm import joinedload
from celery_config import celery
from features.users import models, input_models, exceptions

logging = khLogging.Logger("celery")
app_admins = configuration.AppAdmins()
app_admin_role = configuration.AppAdminRoles()


@celery.task
def seed_admins():
    """
    Adds admin users to the database
    :return:
    """

    with db.connection.get_session() as session:
        for admin in app_admins.admins:
            try:
                current = features.users.operations.create_new_user(
                    user=input_models.RegisterUserInputModel(
                        username=admin["username"],
                        email=admin["email"],
                        password=admin["password"],
                    )
                )
                current.is_email_confirmed = True
                session.add(current)
                session.commit()
                session.refresh(current)
                logging.info(f"Admin #{current.id} was added to the database")
            except features.users.exceptions.UserAlreadyExists:
                continue
    session.close()
    return "Finished adding admins to the database."


@celery.task
def seed_roles():
    """
    Adds admin roles to the database
    :return:
    """

    admin = features.users.operations.get_user_from_db(username=app_admins.admins[0]["username"])
    if not admin:
        return "No admins found to add role"
    with db.connection.get_session() as session:
        role_name = app_admin_role.admin_role
        try:
            role = features.users.operations.create_role(
                name=role_name,
                created_by=admin.id,
            )
            logging.info(f"Role #{role.id} was added to the database")
        except features.users.exceptions.RoleAlreadyExists:
            ...
    session.close()
    return "Finished adding role to the database."


@celery.task
def add_roles_to_admins():
    """
    Adds roles to admins
    :return:
    """

    with db.connection.get_session() as session:
        role = session.query(models.Role).filter(models.Role.name == app_admin_role.admin_role).first()
        if not role:
            session.close()
            return "No roles found to add admins."

        admin_usernames = [admin["username"] for admin in app_admins.admins]
        admins = (
            session.query(models.User)
            .filter(models.User.username.in_(admin_usernames))
            .filter(~models.User.roles.any(models.Role.id == role.id))
            .options(joinedload(models.User.roles))
            .all()
        )
        session.close()

    if not admins:
        return "No admins found to add role."

    added_by = admins[0].id
    for admin in admins:
        features.users.operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=added_by)
        logging.info(f"User #{admin.id} was add to role #{role.id} by #{added_by}")

    return "Finished adding admins to role."


@celery.task
def app_seeder():
    message_seed_admins = seed_admins()
    message_seed_roles = seed_roles()
    message_add_roles_to_admins = add_roles_to_admins()
    return message_seed_admins + os.linesep + message_seed_roles + os.linesep + message_add_roles_to_admins
