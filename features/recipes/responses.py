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


class InstructionResponse(pydantic.BaseModel):
    """Instruction response"""

    id: int
    instruction: str
    category: str
    time: int
    complexity: float
    recipe_id: int


class Recipe(pydantic.BaseModel):
    """Recipe response"""

    id: int
    name: str = pydantic.Field(max_length=255)
    picture: Optional[str]
    summary: Optional[str] = pydantic.Field(max_length=1000)
    calories: Optional[float] = pydantic.Field(default=0, ge=0)
    carbo: Optional[float] = pydantic.Field(default=0, ge=0)
    fats: Optional[float] = pydantic.Field(default=0, ge=0)
    proteins: Optional[float] = pydantic.Field(default=0, ge=0)
    cholesterol: Optional[float] = pydantic.Field(default=0, ge=0)
    time_to_prepare: int = pydantic.Field(gt=0)
    created_by: int
    created_on: datetime.datetime
    updated_by: Optional[str]
    updated_on: datetime.datetime
    category: RecipeCategory | Any = None
    instructions: list[InstructionResponse] | Any = None

    def model_post_init(self, __context: Any):
        if self.category:
            self.category = RecipeCategory(**self.category.__dict__)

        if self.instructions:
            self.instructions = [InstructionResponse(**_.__dict__) for _ in self.instructions]

class Ingredient(pydantic.BaseModel):
    """Ingredient response"""
    id: int
    name: str
    category_id: int
    created_by: int
    created_on: datetime.datetime
    updated_by: Optional[int] = None
    updated_on: Optional[datetime.datetime] = None

class IngredientCategory(pydantic.BaseModel):
    """Ingredient category response"""
    id: int
    name: str
    created_by: int
    created_on: datetime.datetime
    updated_by: Optional[int] = None
    updated_on: Optional[datetime.datetime] = None
    ingredients: list[Ingredient] | Any = None