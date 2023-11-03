from fastapi import HTTPException

from db.connection import get_session

import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import or_

from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

from .input_models import RegisterUserInputModel
from .models import User

# TODO: make secret keys for jwt_secret_key and jwt_refresh_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'JWT_SECRET_KEY'
JWT_REFRESH_SECRET_KEY = 'JWT_REFRESH_SECRET_KEY'
# JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
# JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']


def custom_exception_response(message, error_type: str = "string"):
    return [{"loc": ["string", 0], "msg": message, "type": error_type}]


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def check_password(user: User, password: str) -> bool:
    # Check if passwords match (for login)
    return bcrypt.checkpw(password.encode('utf-8'), user.password)


def set_password(user: RegisterUserInputModel, password: str):
    user.password = hash_password(password=password)


def check_if_user_exists(db: Session, username: str, email: str):
    from features.users.models import User
    return True if db.query(User).filter(or_(User.username == username, User.email == email)).first() \
        else False


def get_user_by_username(db: Session, username: str):
    from features.users.models import User
    return db.query(User).filter(User.username == username).first()


def create_new_user(user: RegisterUserInputModel) -> User:
    # Check if the username or email already exists
    db = get_session()
    if check_if_user_exists(db, user.username, user.email):
        # Raise an HTTPException with the error message
        raise HTTPException(
            status_code=409,
            detail=custom_exception_response(message="User with this username or email already exists!")
        )

    # Validate password
    try:
        RegisterUserInputModel.validate_password(user.password)
    except ValueError as e:
        # Raise an HTTPException with the error message
        raise HTTPException(
            status_code=422,
            detail=custom_exception_response(message=str(e))
        )

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
    current_user = get_user_by_id_username_email(username=username)
    if not current_user or not check_password(current_user, password):
        raise HTTPException(
            status_code=403,
            detail=custom_exception_response(message="Incorrect username or password")
        )


def serialize_users_data(all_users: list):
    # Convert the list of User objects into a dict of dictionaries
    serialized_data = {
        f"{user.id}": {
            # "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in all_users
    }

    return serialized_data


def get_user_by_id_username_email(pk: int = None, username: str = None, email: str = None) -> User | None:
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
    if not query.first():
        raise HTTPException(
            status_code=404,
            detail=custom_exception_response(message="User does not exists", error_type="Not Found")
        )
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
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt
