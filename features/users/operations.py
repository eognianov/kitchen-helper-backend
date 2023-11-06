from starlette.responses import JSONResponse

from db.connection import get_session

import bcrypt

from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

from .exceptions import password_validation_exception, user_already_exist, access_denied
from .input_models import RegisterUserInputModel
from .models import User

import configuration

config = configuration.Config()


def successfully_created_user_response(user: User) -> JSONResponse:
    return JSONResponse(
        content={
            "message": "Successfully created",
            "user_data": {"id": user.id, "username": user.username, "email": user.email}
        },
        status_code=201
    )


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def check_password(user: User, password: str) -> bool:
    # Check if passwords match (for login)
    return bcrypt.checkpw(password.encode('utf-8'), user.password)


def set_password(user: RegisterUserInputModel, password: str):
    user.password = hash_password(password=password)


def create_new_user(user: RegisterUserInputModel) -> User:
    # Check if the username or email already exists
    db = get_session()
    if get_user(username=user.username, email=user.email):
        # Raise an HTTPException with the error message
        user_already_exist()

    # Validate password
    try:
        RegisterUserInputModel.validate_password(user.password)
    except ValueError as e:
        # Raise an HTTPException with the error message
        password_validation_exception(e)

    # Hash the password
    set_password(user, user.password)

    # Create the user in the database
    with get_session() as session:
        db_user = User(username=user.username, email=user.email, password=user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


def signin_user(username: str, password: str):
    # Get user and check if username and password are correct
    current_user = get_user(username=username)
    if not current_user or not check_password(current_user, password):
        access_denied()


def get_user(*, pk: int = None, username: str = None, email: str = None) -> User | None:
    db = get_session()
    query = db.query(User)
    filters = []

    if pk:
        filters.append(User.id == pk)
    elif username:
        filters.append(User.username == username)
    elif email:
        filters.append(User.email == email)

    if filters:
        query = query.filter(*filters)

    return query.first()


def get_all_users():
    db = get_session()
    # Fetch all the users from the db
    all_users = db.query(User).all()

    return all_users


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=config.jwt.access_token_expire_minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.jwt.secret_key, config.jwt.algorithm)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=config.jwt.refresh_token_expire_minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.jwt.refresh_secret_key, config.jwt.algorithm)
    return encoded_jwt
