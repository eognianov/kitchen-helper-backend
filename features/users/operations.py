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
from .models import User, EmailConfirmationToken

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


async def send_email(user: User, token: str):
    # TODO: setup from_email and host in html_content
    message = Mail(
        from_email='your@example.com',
        to_emails=user.email,
        subject='Test Email',
        html_content=(f'Thank you for registering!\n\n Please click the link below to confirm your email:'
                      f'\nhttp://127.0.0.1:8000/users/confirm-email/{token}')
    )

    sg = SendGridAPIClient(api_key=config.grid.send_grid_api_key)

    try:
        response = sg.send(message)
        print(response.status_code)
        return {"message": "Email sent successfully", "status_code": response.status_code}
    except Exception as e:
        print(e)
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


def get_token_from_db(email_confirmation_token: str):
    current_datetime = datetime.utcnow()

    with get_session() as session:
        # Fetch the token object
        token = session.query(EmailConfirmationToken).filter(
            EmailConfirmationToken.email_confirmation_token == email_confirmation_token
        ).first()
        # If token and it is expired delete the token
        if token and token.expired_on < current_datetime:
            session.delete(token)
            session.commit()
            return None

    return token


def confirm_email(user_id: int) -> User:
    user = get_user_from_db(pk=user_id)
    # Mark the user email as confirmed
    user.is_email_confirmed = True
    with get_session() as session:
        # Fetch the token object
        token = session.query(
            EmailConfirmationToken
        ).filter(EmailConfirmationToken.user_id == user.id).first()
        session.delete(token)
        session.commit()
    return user
