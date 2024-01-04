import os

import db.connection
import configuration
import khLogging
import features.users.operations
from sqlalchemy.orm import joinedload
from configuration import celery
from features.users import models, input_models, exceptions

logging = khLogging.Logger("celery-users-tasks")
app_users = configuration.AppUsers()
app_users_role = configuration.AppUsersRoles()


def seed_users() -> str:
    """
    Adds users to the database
    :return:
    """

    with db.connection.get_session() as session:
        for user in app_users.users:
            try:
                current = features.users.operations.create_new_user(
                    user=input_models.RegisterUserInputModel(
                        username=user["username"],
                        email=user["email"],
                        password=user["password"],
                    )
                )
                current.is_email_confirmed = True
                session.add(current)
                session.commit()
                session.refresh(current)
                logging.info(f"User #{current.id} was added to the database")
            except features.users.exceptions.UserAlreadyExists:
                continue
    session.close()
    return "Finished adding users to the database."


def seed_roles() -> str:
    """
    Adds role to the database
    :return:
    """

    user = features.users.operations.get_user_from_db(username=app_users.users[0]["username"])
    if not user:
        return "No users found to add role"
    with db.connection.get_session() as session:
        role_name = app_users_role.role
        try:
            role = features.users.operations.create_role(
                name=role_name,
                created_by=user.id,
            )
            logging.info(f"Role #{role.id} was added to the database")
        except features.users.exceptions.RoleAlreadyExists:
            ...
    session.close()
    return "Finished adding role to the database."


def add_roles_to_users() -> str:
    """
    Adds roles to users
    :return:
    """

    with db.connection.get_session() as session:
        role = session.query(models.Role).filter(models.Role.name == app_users_role.role).first()
        if not role:
            session.close()
            return "No roles found to add users."

        users_usernames = [user["username"] for user in app_users.users]
        users = (
            session.query(models.User)
            .filter(models.User.username.in_(users_usernames))
            .filter(~models.User.roles.any(models.Role.id == role.id))
            .options(joinedload(models.User.roles))
            .all()
        )
        session.close()

    if not users:
        return "No admins found to add role."

    added_by = users[0].id
    for user in users:
        features.users.operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=added_by)
        logging.info(f"User #{user.id} was add to role #{role.id} by #{added_by}")

    return "Finished adding users to role."


@celery.task
def app_seeder() -> str:
    """
    Task for seeding users, user role and adding users to role
    :return:
    """
    message_seed_users = seed_users()
    message_seed_roles = seed_roles()
    message_add_roles_to_users = add_roles_to_users()
    return message_seed_users + os.linesep + message_seed_roles + os.linesep + message_add_roles_to_users
