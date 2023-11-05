from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, func, DATETIME
import datetime
from typing import Optional


class RecipeCategory(DbBaseModel):
    """Recipe category"""
    __tablename__ = "RECIPE_CATEGORIES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(DATETIME, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    updated_on: Mapped[datetime.datetime] = mapped_column(DATETIME, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False)


class Recipe(DbBaseModel):
    """Recipe DB Model"""
    __tablename__ = "RECIPES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fats: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    proteins: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_to_prepare: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(DATETIME, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    updated_on: Mapped[datetime.datetime] = mapped_column(DATETIME, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False)