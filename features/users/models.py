"""
Here we are having only database related classes
"""

from features import DbBaseModel
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column


class User(DbBaseModel):
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    pasword: Mapped[str] = mapped_column(String)
