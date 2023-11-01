import os

import bcrypt
import re
from sqlalchemy.orm import Session
from sqlalchemy import or_

from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

from .input_models import User


# TODO: make secret keys for jwt_secret_key and jwt_refresh_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'JWT_SECRET_KEY'
JWT_REFRESH_SECRET_KEY = 'JWT_REFRESH_SECRET_KEY'
# JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
# JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']


def validate_password(password):
    # Password validation logic
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*?]', password):
        raise ValueError("Password must contain at least one special symbol: !@#$%^&*?")
    return password


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def check_password(user: User, password: str) -> bool:
    # Check if passwords match (for login)
    return bcrypt.checkpw(password.encode('utf-8'), user.password)


def set_password(user: User, password: str):
    user.password = hash_password(password=password)

def check_if_user_exists(db: Session, username: str, email: str):
    from features.users.models import UserOrm
    return True if db.query(UserOrm).filter(or_(UserOrm.username == username, UserOrm.email == email)).first() \
        else False


def get_user_by_username(db: Session, username: str):
    from features.users.models import UserOrm
    return db.query(UserOrm).filter(UserOrm.username == username).first()


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
