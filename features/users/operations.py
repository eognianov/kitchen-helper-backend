from datetime import datetime, timedelta
from typing import Union, Any, Type

import bcrypt
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import update, delete, insert

import configuration
import db.connection
import features.users.exceptions
from db.connection import get_session
from .input_models import RegisterUserInputModel
from .models import User, Role, UserRole

import khLogging

logging = khLogging.Logger.get_child_logger(__file__)

config = configuration.Config()


def _hash_password(password: str) -> bytes:
    """
    Hash password

    :param password:
    :return:
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def check_password(user: User, password: str) -> bool:
    # Check if passwords match (for login)
    return bcrypt.checkpw(password.encode('utf-8'), user.password)


def create_new_user(user: RegisterUserInputModel) -> User:
    # Create the user in the database
    with get_session() as session:
        try:
            # Check if the username or email already exists
            if get_user_from_db(username=user.username, email=user.email):
                raise features.users.exceptions.UserAlreadyExists()
        except features.users.exceptions.UserDoesNotExistException:
            user.password = _hash_password(password=user.password)
            db_user = User(username=user.username, email=user.email, password=user.password)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)

    return db_user


def signin_user(username: str, password: str) -> tuple:
    """
    Validate user password and generate token

    :param username:
    :param password:
    :return:
    """
    current_user = get_user_from_db(username=username)
    if not current_user or not bcrypt.checkpw(password.encode('utf-8'), current_user.password):
        logging.warning(f"Failed logging attempt for {username}")
        features.users.exceptions.AccessDenied()
    return create_token(username)


def get_user_from_db(*, pk: int = None, username: str = None, email: str = None) -> User | None:
    """
    Get user from db

    :param pk:
    :param username:
    :param email:
    :return:
    """
    with get_session() as session:
        query = session.query(User)
        filters = []

        if pk:
            filters.append(User.id == pk)
        elif username:
            filters.append(User.username == username)
        elif email:
            filters.append(User.email == email)

        if filters:
            query = query.filter(*filters)

        user = query.first()
        if not user:
            raise features.users.exceptions.UserDoesNotExistException()

    return user


def get_all_users() -> list:
    """
    Get all users

    :return:
    """
    with get_session() as session:
        all_users = session.query(User).all()

    return all_users


def update_user(user_id: int, field: str, value: str, updated_by: str = '') -> User:
    user = get_user_from_db(pk=user_id)
    with get_session() as session:
        session.execute(update(User), [{"id": user.id, f"{field}": value, "updated_by": updated_by}])
        session.commit()
        user.__setattr__(field, value)
        logging.info(f"User #{user.id} updated. {updated_by} set {field}={value}")
        return user


def create_token(subject: Union[str, Any], expires_delta: timedelta = None, access: bool = True) -> tuple:
    minutes = config.jwt.access_token_expire_minutes if access else config.jwt.refresh_token_expire_minutes
    secret_key = config.jwt.secret_key if access else config.jwt.refresh_secret_key
    algorithm = config.jwt.algorithm
    token_type = "jwt access token" if access else "jwt refresh token"
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm)

    return encoded_jwt, token_type


def get_all_roles() -> list:
    """
        Get all roles

        :return:
    """
    with db.connection.get_session() as session:
        roles = session.query(Role).all()
        return roles


def get_role(pk: int = None, role_name: str = None) -> Role | None:
    """
        Get role by id or name

        :param pk:
        :param role_name:
        :return:
    """
    if not pk and not role_name:
        raise ValidationError("Neither pk nor role_name is provided")

    with db.connection.get_session() as session:
        query = session.query(Role)
        filters = []

        if pk:
            filters.append(Role.id == pk)
        if role_name:
            filters.append(Role.name == role_name)

        if filters:
            query = query.filter(*filters)

        role = query.first()

        if not role:
            raise features.users.exceptions.RoleDoesNotExistException

    return role


def check_user_role(user_id: int, role_id: int) -> bool:
    """
        Create role

        :param user_id:
        :param role_id:
        :return:
    """

    user = get_user_from_db(pk=user_id)
    role = get_role(pk=role_id)
    if role not in user.roles:
        return False

    return True


def create_role(name: str, created_by: str = 'me') -> Role:
    """
        Create role

        :param name:
        :param created_by:
        :return:
    """
    try:
        role = get_role(role_name=name)
        if role:
            raise features.users.exceptions.RoleAlreadyExists
    except features.users.exceptions.RoleDoesNotExistException:
        with db.connection.get_session() as session:
            role = Role(name=name, created_by=created_by)
            session.add(role)
            session.commit()
            session.refresh(role)
        logging.info(f"Role {name} with #{role.id} was created by #{created_by}")
        return role


def add_user_to_role(user_id: int, role_id: int, added_by: str = 'me') -> None:
    """
        Assign role to user

        :param user_id:
        :param role_id:
        :param added_by:
        :return:
    """
    user = get_user_from_db(pk=user_id)
    role = get_role(pk=role_id)

    if check_user_role(user_id, role_id):
        raise features.users.exceptions.UserWithRoleExist

    with db.connection.get_session() as session:
        user_role = UserRole(user_id=user.id, role_id=role.id, added_by=added_by)
        session.add(user_role)
        session.commit()
    logging.info(f"User #{user.id} was add to role #{role.id} by #{added_by}")


def remove_user_from_role(user_id: int, role_id: int) -> None:
    """
        Remove user from role

        :param user_id:
        :param role_id:
        :return:
    """
    user = get_user_from_db(pk=user_id)
    role = get_role(pk=role_id)

    if not check_user_role(user_id, role_id):
        raise features.users.exceptions.UserWithRoleDoesNotExist

    with db.connection.get_session() as session:
        if role in user.roles:
            user.roles.remove(role)

        session.add(user)
        session.commit()
    logging.info(f"User #{user.id} was add to role #{role.id} by #{added_by}")
