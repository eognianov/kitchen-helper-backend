from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, func, ForeignKey, DateTime
import datetime
from typing import Optional


class RecipeCategory(DbBaseModel):
    """Recipe category"""
    __tablename__ = "RECIPE_CATEGORIES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False)
    recipes: Mapped[list["Recipe"]] = relationship("Recipe", back_populates="category", init=False)


class Recipe(DbBaseModel):
    """Recipe DB Model"""
    __tablename__ = "RECIPES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, init=False)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, init=False)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True, init=False)
    carbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True, init=False)
    fats: Mapped[Optional[float]] = mapped_column(Float, nullable=True, init=False)
    proteins: Mapped[Optional[float]] = mapped_column(Float, nullable=True, init=False)
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True, init=False)
    time_to_prepare: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("RECIPE_CATEGORIES.id"), nullable=True, init=False)
    category: Mapped[RecipeCategory] = relationship("RecipeCategory", back_populates="recipes", init=False)