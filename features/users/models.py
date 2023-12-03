import datetime
from typing import Optional

from sqlalchemy import String, LargeBinary, Column, Table, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from features import DbBaseModel


class User(DbBaseModel):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary())
    # TODO add updated by and update on

    roles = relationship('Role', secondary='user_roles', back_populates='users', lazy='selectin')

    @property
    def user_role_ids(self) -> list[int]:
        """Return list of roles ids"""

        return [_.id for _ in self.roles]


class Role(DbBaseModel):
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

