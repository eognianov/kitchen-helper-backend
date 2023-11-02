"""
Here we are having all the business logic
Only here you need to work with db
"""
from .input_models import CreateUserInputModel
from .models import User
import db.connection
from sqlalchemy import select


def create_user(user_inout_model: CreateUserInputModel) -> User:
    # check if user exists
    # hash input_model password directly to it
    user_inout_model.password = hash_password(user_inout_model.password)
    new_user = User(**user_inout_model.model_dump())
    with db.connection.get_session() as session:
        session.add(new_user)
        session.refresh(new_user)
        session.commit()
    return new_user


def hash_password(password: str) -> str:
    pass


def login(username: str, password: str):
    with db.connection.get_session() as session:
        user = session.execute(select(User).where(User.username==username and User.pasword == hash_password(password)))
        if user:
            # successful login
            pass
        else:
            # loging error
            pass