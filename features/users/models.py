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

    roles = relationship('Role', secondary='user_roles', back_populates='users', lazy='selectin')


class Role(DbBaseModel):
    __tablename__ = 'Roles'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    created_by: Mapped[str] = mapped_column(String(30))

    users = relationship('User', secondary='user_roles', back_populates='roles', lazy='selectin')


user_roles = Table('user_roles', DbBaseModel.metadata,
                   Column('user_id', ForeignKey('Users.id'), primary_key=True),
                   Column('role_id', ForeignKey('Roles.id'), primary_key=True),
                   Column('added_by', String(50)),
                   Column('added_on', DateTime, server_default=func.current_timestamp())
                   )


# class UserRole(DbBaseModel):
#     __tablename__ = 'UserRole'
#     user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
#     role_id = Column(Integer, ForeignKey('Roles.id'), nullable=False)
#     added_by = Column(String(50))
#     added_on = mapped_column(DateTime, server_default=func.current_timestamp())
#
#     user = relationship('User', back_populates='roles')
#     role = relationship('Role', back_populates='users')
