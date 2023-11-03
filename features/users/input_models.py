from pydantic import BaseModel, constr, EmailStr

import re
import configuration

config = configuration.Config()


class RegisterUserInputModel(BaseModel):
    # id: int
    username: constr(min_length=3, max_length=30)
    email: EmailStr  # EmailStr for email validation
    password: constr()

    @staticmethod
    def validate_password_dev(password):
        # Password validation logic for 'dev' context
        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters long in 'dev' context")

    @staticmethod
    def validate_password_prod(password):
        # Password validation logic for 'prod' context
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

    @staticmethod
    def validate_password(password, context=config.context):
        if context == 'dev':
            RegisterUserInputModel.validate_password_dev(password)
        else:
            RegisterUserInputModel.validate_password_prod(password)
        return password


class UsersResponseModel(BaseModel):
    _id: int
    username: str
    email: str
