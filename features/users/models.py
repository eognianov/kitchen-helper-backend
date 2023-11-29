import datetime
from typing import Optional

from sqlalchemy import String, LargeBinary, Column, Table, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, LargeBinary, ForeignKey, Boolean, DateTime, func
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
    expired_on: Mapped[datetime.datetime] = mapped_column(DateTime)

    roles = relationship('Role', secondary='user_roles', back_populates='users', lazy='selectin')


class Role(DbBaseModel):
    """Password reset token DB model"""
    __tablename__ = 'Roles'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    created_by: Mapped[str] = mapped_column(String(30), nullable=True)

    users = relationship('User', secondary='user_roles', back_populates='roles', lazy='selectin')


class UserRole(DbBaseModel):
    __tablename__ = 'user_roles'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('Users.id', ondelete='RESTRICT'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('Roles.id', ondelete='RESTRICT'), primary_key=True)
    added_by: Mapped[str] = mapped_column(String(50))
    added_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)

    expired_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), nullable=False)
