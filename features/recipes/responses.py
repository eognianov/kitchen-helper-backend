"""Recipes feature responses"""
import datetime
from typing import Optional, Any
import pydantic


class Category(pydantic.BaseModel):
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


class RecipeResponse(pydantic.BaseModel):
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
    updated_by: Optional[int]
    updated_on: datetime.datetime
    category: Category | Any = None
    instructions: list[InstructionResponse] | Any = None

    def model_post_init(self, __context: Any):
        if self.category:
            self.category = Category(**self.category.__dict__)

        if self.instructions:
            self.instructions = [InstructionResponse(**_.__dict__) for _ in self.instructions]


class PageResponse(pydantic.BaseModel):
    """Recipe pagination and filtering response"""
    page_number: int
    page_size: int
    previous_page: int | None
    next_page: int | None
    total_pages: int
    total_items: int
    recipes: list[RecipeResponse]
