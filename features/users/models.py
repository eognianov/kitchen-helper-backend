from pydantic import field_validator
from sqlalchemy import String, LargeBinary, ForeignKey, Boolean, DateTime, func, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from features import DbBaseModel

import datetime

from features.users.constants import TokenTypes


class User(DbBaseModel):
    """User DB model"""
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary())
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class Token(DbBaseModel):
    """Token DB model"""
    __tablename__ = 'CONFIRMATION_TOKEN'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    token: Mapped[str] = mapped_column(String(43), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"), nullable=False)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    expired_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), nullable=False)
