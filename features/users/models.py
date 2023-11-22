from sqlalchemy import String, LargeBinary, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from features import DbBaseModel

import datetime


class User(DbBaseModel):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary())
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class EmailConfirmationToken(DbBaseModel):
    __tablename__ = 'TOKEN'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email_confirmation_token: Mapped[str] = mapped_column(String(43), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    expired_on: Mapped[datetime.datetime] = mapped_column(DateTime)


class PasswordResetToken(DbBaseModel):
    __tablename__ = 'PASSWORD_TOKEN'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    reset_token: Mapped[str] = mapped_column(String(43), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    expired_on: Mapped[datetime.datetime] = mapped_column(DateTime)
