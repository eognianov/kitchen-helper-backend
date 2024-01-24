from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
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
    picture: Mapped[int] = mapped_column(ForeignKey("IMAGES.id"), default=None, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, default=None)
    serves: Mapped[int] = mapped_column(Integer, default=1, server_default='1')
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
        "RecipeIngredient",
        lazy="selectin",
        primaryjoin="Recipe.id == RecipeIngredient.recipe_id",
    )

    @hybrid_property
    def calories(self) -> float:
        calories = 0
        for ingredient_mapping in self.ingredients:
            calories += ingredient_mapping.quantity * ingredient_mapping.ingredient.calories
        return calories

    @hybrid_property
    def carbo(self) -> float:
        carbo = 0
        for ingredient_mapping in self.ingredients:
            carbo += ingredient_mapping.quantity * ingredient_mapping.ingredient.carbo
        return carbo

    @hybrid_property
    def fats(self) -> float:
        fats = 0
        for ingredient_mapping in self.ingredients:
            fats += ingredient_mapping.quantity * ingredient_mapping.ingredient.fats
        return fats

    @hybrid_property
    def proteins(self) -> float:
        protein = 0
        for ingredient_mapping in self.ingredients:
            protein += ingredient_mapping.quantity * ingredient_mapping.ingredient.protein
        return protein

    @hybrid_property
    def cholesterol(self) -> float:
        cholesterol = 0
        for ingredient_mapping in self.ingredients:
            cholesterol += ingredient_mapping.quantity * ingredient_mapping.ingredient.cholesterol
        return cholesterol

    @hybrid_property
    def complexity(self) -> float:
        if not self.instructions:
            return 0
        return round(sum(_.complexity for _ in self.instructions) / len(self.instructions), 1)

    @hybrid_property
    def time_to_prepare(self) -> int:
        return sum(_.time for _ in self.instructions)

    def to_dict(self):
        """
        Parse the model to dictionary, including the hybrid_properties as well
        :return:
        """

        _model_dict = self.__dict__
        _model_dict['calories'] = self.calories
        _model_dict['carbo'] = self.carbo
        _model_dict['fats'] = self.fats
        _model_dict['proteins'] = self.proteins
        _model_dict['cholesterol'] = self.cholesterol
        _model_dict['complexity'] = self.complexity
        _model_dict['time_to_prepare'] = self.time_to_prepare
        return _model_dict


class RecipeInstruction(DbBaseModel):
    """Recipe instruction"""

    __tablename__ = "RECIPE_INSTRUCTIONS"

    id: Mapped[int] = mapped_column(Integer, init=False, autoincrement=True, primary_key=True)
    instruction: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(100))
    time: Mapped[int] = mapped_column(Integer)
    complexity: Mapped[float] = mapped_column(Float)

    recipe_id: Mapped[int] = mapped_column(ForeignKey('RECIPES.id'), nullable=True, init=False)
    recipe: Mapped[Recipe] = relationship('Recipe', back_populates='instructions', init=False, lazy='selectin')
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("Users.id"), nullable=True, init=False)
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), init=False
    )
    audio_file: Mapped[str] = mapped_column(String(500), nullable=True, init=False)


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


class RecipeIngredient(DbBaseModel):
    """RecipeIngredient DB model"""

    __tablename__ = 'RECIPE_INGREDIENTS_MAPPING'

    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey('RECIPES.id'), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey('INGREDIENTS.id'), primary_key=True)
    ingredient = relationship(
        "Ingredient",
        lazy="selectin",
        primaryjoin="RecipeIngredient.ingredient_id == Ingredient.id",
    )
    quantity: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
