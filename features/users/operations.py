import os
import secrets

from sqlalchemy import update

import features.users.exceptions
from db.connection import get_session

import bcrypt
import datetime

from datetime import datetime, timedelta
from typing import Union, Any, Type

import bcrypt
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import update, delete, insert
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .input_models import RegisterUserInputModel
from .models import User, Token
from .constants import TokenTypes

import configuration
import db.connection
import features.users.exceptions
from db.connection import get_session
from .input_models import RegisterUserInputModel
from .models import User, Role, UserRole


def hash_password(password: str) -> bytes:
    """
    Hash the password
    :param password:
    :return:
    """

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def check_password(user: User, password: str) -> bool:
    """
    Check if passwords match (for login)

    :param user:
    :param password:
    :return:
    """

    return bcrypt.checkpw(password.encode('utf-8'), user.password)


def create_new_user(user: RegisterUserInputModel) -> User:
    """
    Create user and send confirmations email

    :param user:
    :return:
    """

    with get_session() as session:

        if get_user_from_db(username=user.username, email=user.email):
            raise features.users.exceptions.UserAlreadyExists()

        user.password = hash_password(password=user.password)
        db_user = User(username=user.username, email=user.email, password=user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        features.users.operations.generate_email_password_token(
            db_user,
            token_type=TokenTypes.EMAIL_CONFIRMATION
        )

    return db_user


def signin_user(username: str, password: str) -> tuple:
    """Get user and check if username and password are correct"""

    current_user = get_user_from_db(username=username)
    if not current_user or not check_password(current_user, password):
        features.users.exceptions.AccessDenied()

    return create_token(username)


def get_user_from_db(*, pk: int = None, username: str = None, email: str = None) -> User | None:
    """
    Get user from DB by pk, username or email

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
    """Fetch all the users from the DB"""

    with get_session() as session:
        all_users = session.query(User).all()

    return all_users


def update_user(user_id: int, field: str, value: str, updated_by: int = 1) -> Type[User]:
    """
    Update user

    :param user_id:
    :param field:
    :param value:
    :param updated_by:
    :return:
    """

    user = get_user_from_db(pk=user_id)
    with get_session() as session:
        session.execute(update(User), [{"id": user.id, f"{field}": value, "updated_by": updated_by}])
        session.commit()
        return session.query(User).where(User.id == user_id).first()


def create_token(subject: Union[str, Any], expires_delta: timedelta = None, access: bool = True) -> tuple:
    """
    Create JWT Token

    :param subject:
    :param expires_delta:
    :param access:
    :return:
    """

    jwt_config = configuration.JwtToken()

    minutes = jwt_config.access_token_expire_minutes if access else jwt_config.refresh_token_expire_minutes
    secret_key = jwt_config.secret_key if access else jwt_config.refresh_secret_key
    algorithm = jwt_config.algorithm
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
        user_role = UserRole(user_id=user_id, role_id=role_id, added_by=added_by)
        session.add(user_role)
        session.commit()


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


async def send_email(*, subject: str, content: str, recipient: str):
def send_email(*, token_type: str, token: str, recipient: User):
    """
    Send email for email confirmation or reset password

    :param token_type:
    :param token:
    :param recipient:
    """

    config = configuration.Config()
    send_grid = configuration.SendGrid()

    email_subject = ''
    email_content = ''

    if token_type == TokenTypes.EMAIL_CONFIRMATION:
        email_content = features.users.constants.EmailDetails.EMAIL_CONFIRMATION_CONTENT.format(
            recipient.username,
            config.server.host,
            config.server.port,
            token
        )
        email_subject = features.users.constants.EmailDetails.EMAIL_CONFIRMATION_SUBJECT

    elif token_type == TokenTypes.PASSWORD_RESET:
        email_content = features.users.constants.EmailDetails.PASSWORD_RESET_CONTENT.format(
            recipient.username,
            config.server.host,
            config.server.port,
            token
        )
        email_subject = features.users.constants.EmailDetails.PASSWORD_RESET_SUBJECT

    message = Mail(
        from_email='dimitrov.mitko.md@gmail.com',
        to_emails=recipient.email,
        subject=email_subject,
        html_content=email_content
    )

    sg = SendGridAPIClient(api_key=send_grid.send_grid_api_key)

    try:
        response = sg.send(message)
        return {"message": "Email sent successfully", "status_code": response.status_code}
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}


def generate_email_password_token(user: User, token_type: str):
    """
    Generate email confirmation token or password reset token
    Send email to the user

    :param user:
    :param token_type:
    :return:
    """

    confirmation_token = configuration.ConfirmationToken()

    expiration_minutes = None

    if token_type == TokenTypes.EMAIL_CONFIRMATION:
        expiration_minutes = confirmation_token.email_token_expiration
    elif token_type == TokenTypes.PASSWORD_RESET:
        expiration_minutes = confirmation_token.password_token_expiration

    token = secrets.token_urlsafe(32)

    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)

    with get_session() as session:
        token_obj = Token(
            token=token,
            user_id=user.id,
            expired_on=expiration_time,
            token_type=token_type
        )

        session.add(token_obj)
        session.commit()

    send_email(token_type=token_type, token=token, recipient=user)

    return token


def check_if_token_is_valid(token: str):
    """
    Get the token from db if exists, check if token is expired

    :param token:
    :return:
    """

    current_datetime = datetime.utcnow()

    with get_session() as session:
        token = (
            session.query(Token)
            .filter(Token.token == token, Token.expired_on > current_datetime)
            .first()
        )

    return token or None


def confirm_email(token: Type[Token]) -> User:
    """
    Mark the user email as confirmed and delete the token

    :param token:
    :return:
    """
    with get_session() as session:
        user = get_user_from_db(pk=token.user_id)
        user.is_email_confirmed = True
        token.expired_on = datetime.utcnow()
        session.add(user)
        session.add(token)
        session.commit()

    return user


def update_user_password(user: User, new_password: str) -> User:
    """
    Validate the new password
    Check if the new password does not match the old password
    Hash the new password
    Change the password for the requested user and expire the token

    :param user:
    :param new_password:
    :return:
    """

    RegisterUserInputModel.validate_password(new_password)

    if check_password(user, new_password):
        raise features.users.exceptions.SamePasswordsException()

    hashed_password = hash_password(new_password)
    user.password = hashed_password

    with get_session() as session:
        token = session.query(
            Token
        ).filter(Token.user_id == user.id).first()
        token.expired_on = datetime.utcnow()
        session.add(user)
        session.add(token)
        session.commit()

    return user
