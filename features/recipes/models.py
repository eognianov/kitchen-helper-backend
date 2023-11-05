from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Enum, Float, DateTime, func, DATETIME
import datetime


class RecipeCategory(DbBaseModel):
    """Recipe category"""
    __tablename__ = "RECIPE_CATEGORIES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(DATETIME, server_default=func.current_timestamp())
