import secrets

from sqlalchemy import update

import features.users.exceptions
from db.connection import get_session

import bcrypt
import datetime

from datetime import datetime, timedelta
from typing import Union, Any, Type
from jose import jwt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .input_models import RegisterUserInputModel
from .models import User, EmailConfirmationToken, PasswordResetToken

import configuration

config = configuration.Config()


def hash_password(password: str) -> bytes:
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
                # Raise an Exception
                raise features.users.exceptions.UserAlreadyExists()
        except features.users.exceptions.UserDoesNotExistException:
            # Create the new user
            user.password = hash_password(password=user.password)
            db_user = User(username=user.username, email=user.email, password=user.password)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)

    return db_user


def signin_user(username: str, password: str) -> tuple:
    # Get user and check if username and password are correct
    current_user = get_user_from_db(username=username)
    if not current_user or not check_password(current_user, password):
        features.users.exceptions.AccessDenied()
    # Create jwt token
    return create_token(username)


def get_user_from_db(*, pk: int = None, username: str = None, email: str = None) -> User | None:
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
    with get_session() as session:
        # Fetch all the users from the db
        all_users = session.query(User).all()

    return all_users


def update_user(user_id: int, field: str, value: str, updated_by: str = '') -> Type[User]:
    user = get_user_from_db(pk=user_id)
    with get_session() as session:
        session.execute(update(User), [{"id": user.id, f"{field}": value, "updated_by": updated_by}])
        session.commit()
        return session.query(User).where(User.id == user_id).first()


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


async def send_email(*, subject: str, content: str, recipient: str):
    # TODO: setup from_email
    message = Mail(
        from_email='your@example.com',
        to_emails=recipient,
        subject=subject,
        html_content=content
    )

    sg = SendGridAPIClient(api_key=config.grid.send_grid_api_key)

    try:
        response = sg.send(message)
        return {"message": "Email sent successfully", "status_code": response.status_code}
    except Exception as e:
        return {"message": "An error occurred", "error": str(e)}


def generate_email_confirmation_token(user: User, expiration_days: int = 7):
    token = secrets.token_urlsafe(32)

    # Calculate the expiration datetime
    expiration_time = datetime.utcnow() + timedelta(days=expiration_days)

    with get_session() as session:
        token_obj = EmailConfirmationToken(
            email_confirmation_token=token,
            user_id=user.id,
            expired_on=expiration_time
        )
        session.add(token_obj)
        session.commit()

    return token


def get_token_from_db(token: str, token_type: str):
    # Get the token from db if exists, check if token is expired and delete it

    model = EmailConfirmationToken if token_type == 'email' else PasswordResetToken
    current_datetime = datetime.utcnow()

    with get_session() as session:
        # Fetch the token object
        token = session.query(model).filter(
            model.email_confirmation_token == token
        ).first() if token_type == 'email' else session.query(model).filter(
            model.reset_token == token
        ).first()
        # If token and it is expired delete the token
        if token and token.expired_on < current_datetime:
            session.delete(token)
            session.commit()
            return None

    return token


def confirm_email(user_id: int) -> User:
    # Mark the user email as confirmed and delete the token

    user = get_user_from_db(pk=user_id)
    user.is_email_confirmed = True

    with get_session() as session:
        token = session.query(
            EmailConfirmationToken
        ).filter(EmailConfirmationToken.user_id == user.id).first()
        session.delete(token)
        session.commit()

    return user


def generate_password_reset_token(user: User, expiration_hours: int = 1) -> str:
    # Generate password reset token and set expiration time

    token = secrets.token_urlsafe(32)
    expiration_time = datetime.utcnow() + timedelta(hours=expiration_hours)

    with get_session() as session:
        reset_token = PasswordResetToken(
            user_id=user.id,
            reset_token=token,
            expired_on=expiration_time
        )
        session.add(reset_token)
        session.commit()

    return token


def update_user_password(user: User, new_password: str) -> User:
    # Check if the new password does not match the old password
    # Hash the new password
    # Change the password for the requested user and delete the token

    if check_password(user, new_password):
        raise features.users.exceptions.SamePasswordsException()

    hashed_password = hash_password(new_password)
    user.password = hashed_password

    with get_session() as session:
        token = session.query(
            PasswordResetToken
        ).filter(PasswordResetToken.user_id == user.id).first()
        session.delete(token)
        session.commit()

    return user
