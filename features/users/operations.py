from sqlalchemy import update

import features.users.exceptions
from db.connection import get_session

import bcrypt

from datetime import datetime, timedelta
from typing import Union, Any, Type
from jose import jwt

from .input_models import RegisterUserInputModel
from .models import User

import configuration
from .responses import JwtTokenResponseModel

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


def signin_user(username: str, password: str) -> JwtTokenResponseModel:
    # Get user and check if username and password are correct
    current_user = get_user_from_db(username=username)
    if not current_user or not check_password(current_user, password):
        features.users.exceptions.AccessDenied()
    # Create jwt token
    token, token_type = create_token(username)
    return JwtTokenResponseModel(token_value=token, token_type=token_type)


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


def get_all_users():

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


def create_token(subject: Union[str, Any], expires_delta: timedelta = None, access: bool = True) -> JwtTokenResponseModel:
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

    return JwtTokenResponseModel(token_value=encoded_jwt, token_type=token_type)
