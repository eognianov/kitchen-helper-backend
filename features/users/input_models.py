"""Users feature input model"""
import re

from email_validator import validate_email
from pydantic import BaseModel, EmailStr, Field, field_validator

import configuration

config = configuration.Config()


class RegisterUserInputModel(BaseModel):
    """Create user"""
    username: str = Field(min_length=3, max_length=30)
    email: str = EmailStr
    password: str = Field()

    @field_validator('email', mode='after')
    @classmethod
    def validate_user_email(cls, email):
        try:
            validate_email(email)
        except Exception as e:
            raise ValueError(f"Invalid email address: {e}")

        return email

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

        return password


class UpdateUserInputModel(BaseModel):
    """Update email"""
    field: str
    value: str

    @field_validator('field')
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = [
            'EMAIL'
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        return field

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: str):
        try:
            validate_email(value)
        except Exception as e:
            raise ValueError(f"Invalid email address: {e}")

        return value


class CreateUserRole(BaseModel):
    name: str


class AddRoleToUser(BaseModel):
    user_id: int
    role_id: int
    added_by: str


class RemoveRoleFromUser(BaseModel):
    user_id: int
    role_id: int
