import enum

from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, func, ForeignKey, DateTime, Boolean
import datetime
from typing import Optional


class IngredientCategory(DbBaseModel):

    """Ingredient category model"""

    __tablename__ = "INGREDIENT_CATEGORIES"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, init=False
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), init=False
    )

    updated_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("Users.id"), nullable=True, init=False
    )

    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        init=False,
    )

    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient", back_populates="ingredient", init=False, lazy="selectin"
    )


class MeasurementUnits(enum.Enum):
    kg = enum.auto()
    ml = enum.auto()
    g = enum.auto()
    l = enum.auto()
    oz = enum.auto()
    lb = enum.auto()
    cup = enum.auto()


class Ingredient(DbBaseModel):
    __tablename__ = "INGREDIENTS"

    id: Mapped[int] = mapped_column(Integer, init=False, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    carbo: Mapped[float] = mapped_column(Float, nullable=False)
    fats: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=False)
    cholesterol: Mapped[float] = mapped_column(Float, nullable=False)
    measurement: Mapped[str] = mapped_column(String(100), nullable=False)
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    deleted_on: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, init=False
    )
    deleted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)

class RecipeCategory(DbBaseModel):
    """Recipe category"""
    __tablename__ = "RECIPE_CATEGORIES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(),
                                                          onupdate=func.current_timestamp(), init=False)
    recipes: Mapped[list["Recipe"]] = relationship("Recipe", back_populates="category", init=False, lazy="selectin")


class Recipe(DbBaseModel):
    """Recipe DB Model"""
    __tablename__ = "RECIPES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    time_to_prepare: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)
    updated_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(),
                                                          onupdate=func.current_timestamp(), init=False)
    category: Mapped[RecipeCategory] = relationship("RecipeCategory", back_populates="recipes", default=None,
                                                    lazy="selectin")
    category_id: Mapped[int] = mapped_column(ForeignKey("RECIPE_CATEGORIES.id"), nullable=True, default=None)
    picture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, default=None)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    carbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    fats: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    proteins: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    complexity: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    instructions: Mapped[list["RecipeInstruction"]] = relationship("RecipeInstruction", back_populates="recipe",
                                                           init=False, lazy='selectin')
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, default=None)
    published_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, default=None)
    deleted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)


class RecipeInstruction(DbBaseModel):
    """Recipe instruction"""
    __tablename__ = "RECIPE_INSTRUCTIONS"

    id: Mapped[int] = mapped_column(Integer, init=False, autoincrement=True, primary_key=True)
    instruction: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(100))
    time: Mapped[int] = mapped_column(Integer)
    complexity: Mapped[float] = mapped_column(Float)

    recipe_id: Mapped[int] = mapped_column(ForeignKey('RECIPES.id'), nullable=False, init=False)
    recipe: Mapped[Recipe] = relationship('Recipe', back_populates='instructions', init=False, lazy='selectin')

