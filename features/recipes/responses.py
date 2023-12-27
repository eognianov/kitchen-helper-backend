"""Recipes feature responses"""
import datetime
from typing import Optional, Any

import pydantic


class RecipeCategory(pydantic.BaseModel):
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


class RecipeResponse(pydantic.BaseModel):
    """Recipe response"""

    id: int
    name: str = pydantic.Field(max_length=255)
    picture: Optional[str]
    summary: Optional[str]
    calories: Optional[float]
    carbo: Optional[float]
    fats: Optional[float]
    proteins: Optional[float]
    cholesterol: Optional[float]
    time_to_prepare: int
    complexity: int = 0
    created_by: int = 0
    created_on: datetime.datetime
    updated_by: Optional[int]
    updated_on: datetime.datetime

    category: CategoryShortResponse | Any = None
    instructions: list[InstructionResponse] | Any = None

    def model_post_init(self, __context: Any):
        if self.category:
            self.category = CategoryShortResponse(**self.category.__dict__)

        if self.instructions:
            self.instructions = [InstructionResponse(**_.__dict__) for _ in self.instructions]


class PSFRecipesResponseModel(pydantic.BaseModel):
    """Recipe pagination, sorting, and filtering response"""

    page_number: int
    page_size: int
    previous_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int
    recipes: list[RecipeResponse]


class IngredientResponse:
    """Ingredient response"""

    id: int
    name: str
    calories: float
    carbo: float
    fats: float
    protein: float
    cholesterol: float
    measurement: str
    is_deleted: Optional[bool] = False
    deleted_on: Optional[datetime.datetime] = None
    deleted_by: Optional[int] = None

    category: CategoryShortResponse = None

    class Config:
        arbitrary_types_allowed = True


# class PSFRIngredientsResponseModel(pydantic.BaseModel):
#     """Ingredients pagination, sorting, and filtering response"""
#
#     page_number: int
#     page_size: int
#     previous_page: str | None
#     next_page: str | None
#     total_pages: int
#     total_items: int
#     # ingredients: list[IngredientResponse]
#     ingredients: list[IngredientResponse] | Any = None
#


class IngredientCategory(pydantic.BaseModel):
    """Ingredient category response"""

    id: int
    name: str
    created_by: int
    created_on: datetime.datetime
    updated_by: Optional[int] = None
    updated_on: Optional[datetime.datetime] = None
    ingredients: list[IngredientResponse] | Any = None
