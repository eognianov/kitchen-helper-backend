from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, func, ForeignKey, DateTime, Boolean, Numeric
import datetime
from typing import Optional


class RecipeCategory(DbBaseModel):
    """Recipe category"""

    __tablename__ = "RECIPE_CATEGORIES"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False
    )
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
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False
    )
    category: Mapped[RecipeCategory] = relationship(
        "RecipeCategory", back_populates="recipes", default=None, lazy="selectin"
    )
    category_id: Mapped[int] = mapped_column(ForeignKey("RECIPE_CATEGORIES.id"), nullable=True, default=None)
    picture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, default=None)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    carbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    fats: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    proteins: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    complexity: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    instructions: Mapped[list["RecipeInstruction"]] = relationship(
        "RecipeInstruction", back_populates="recipe", init=False, lazy='selectin'
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, default=None)
    published_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, default=None)
    deleted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, default=None)
    ingredients = relationship(
        "Ingredient",
        secondary="recipe_ingredients",
        back_populates="recipes",
        lazy="selectin",
        primaryjoin="Recipe.id == RecipeIngredient.recipe_id",
        secondaryjoin="Ingredient.id == RecipeIngredient.ingredient_id",
    )


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


class Ingredient(DbBaseModel):
    """Ingredient DB model"""

    __tablename__ = "INGREDIENTS"

    id: Mapped[int] = mapped_column(Integer, init=False, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    calories: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carbo: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fats: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    cholesterol: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    measurement: Mapped[str] = mapped_column(String(25), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False
    )
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    deleted_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, init=False)
    deleted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, init=False)
    recipes = relationship(
        "Recipe",
        secondary="recipe_ingredients",
        back_populates="ingredients",
        lazy="selectin",
        primaryjoin="Ingredient.id == RecipeIngredient.ingredient_id",
        secondaryjoin="Recipe.id == RecipeIngredient.recipe_id",
    )


class RecipeIngredient(DbBaseModel):
    """RecipeIngredient DB model"""

    __tablename__ = 'recipe_ingredients'

    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey('RECIPES.id'), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey('INGREDIENTS.id'), primary_key=True)
    quantity: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
