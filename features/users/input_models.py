from pydantic import BaseModel, EmailStr, Field, field_validator

import re
import configuration

config = configuration.Config()


class RegisterUserInputModel(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str = EmailStr  # for email validation
    password: str = Field()

    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, password):
        if config.context == configuration.ContextOptions.DEV:
            if len(password) < 4:
                raise ValueError("Password must be at least 4 characters long in 'dev' context")
        else:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            if not re.search(r'[A-Z]', password):
                raise ValueError("Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                raise ValueError("Password must contain at least one lowercase letter")
            if not re.search(r'[0-9]', password):
                raise ValueError("Password must contain at least one digit")
            if not re.search(r'[!@#$%^&?]', password):
                raise ValueError("Password must contain at least one special symbol: !@#$%^&?")


class UsersResponseModel(BaseModel):
    id: int
    username: str
    email: str
