"""Recipes feature responses"""
import datetime
from typing import Optional, Any

import pydantic

from features.recipes.models import Recipe
from features.recipes import helpers


class Category(pydantic.BaseModel):
    """Category response"""

    id: int
    name: str
    created_by: int
    created_on: datetime.datetime
    updated_by: Optional[int] = None
    updated_on: Optional[datetime.datetime] = None


class CategoryShortResponse(pydantic.BaseModel):
    """Category response"""

    id: int
    name: str


class InstructionResponse(pydantic.BaseModel):
    """Instruction response"""

    id: int
    instruction: str
    category: str
    time: int
    complexity: float
    recipe_id: int


class IngredientResponse(pydantic.BaseModel):
    """Ingredient response"""

    id: int
    name: str
    calories: float
    carbo: float
    fats: float
    protein: float
    cholesterol: float
    measurement: str
    category: str


class RecipeIngredientResponse(pydantic.BaseModel):
    id: int
    name: str
    measurement: str
    quantity: float


class RecipeResponse(pydantic.BaseModel):
    """Recipe response"""

    id: int
    name: str = pydantic.Field(max_length=255)
    picture: Optional[int]
    summary: Optional[str]
    serves: Optional[int]
    calories: float = 0.0
    carbo: float = 0.0
    fats: float = 0.0
    proteins: float = 0.0
    cholesterol: float = 0.0
    time_to_prepare: int = 0
    complexity: float = 0
    created_by: int = 0
    created_on: datetime.datetime
    updated_by: Optional[int]
    updated_on: datetime.datetime
    is_published: bool = False
    published_on: Optional[datetime.datetime]
    published_by: Optional[int]

    category: CategoryShortResponse | Any = None
    instructions: list[InstructionResponse] | Any = None
    ingredients: list[RecipeIngredientResponse] | Any = None

    def model_post_init(self, __context: Any):
        if self.category:
            self.category = CategoryShortResponse(**self.category.__dict__)

        if self.instructions:
            self.instructions = [InstructionResponse(**_.__dict__) for _ in self.instructions]

        if self.ingredients:
            self.ingredients = [
                RecipeIngredientResponse(
                    id=ingredient_mapping.ingredient.id,
                    name=ingredient_mapping.ingredient.name,
                    quantity=ingredient_mapping.quantity,
                    measurement=ingredient_mapping.ingredient.measurement,
                )
                for ingredient_mapping in self.ingredients
            ]


class PSFRecipesResponseModel(pydantic.BaseModel):
    """Recipe pagination, sorting, and filtering response"""

    page_number: int
    page_size: int
    previous_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int
    recipes: list[RecipeResponse]
