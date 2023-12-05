"""Recipes feature responses"""
import datetime
from typing import Optional, Any
import pydantic
from pydantic import validator


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
    complexity: int
    created_by: int
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


class PageResponse(pydantic.BaseModel):
    """Recipe pagination and filtering response"""
    page_number: int
    page_size: int
    previous_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int
    recipes: list[RecipeResponse]

    def __post_init__(self):
        [print('*' * 50) for _ in range(5)]
        self.previous_page = 'previous page'
        self.next_page = 'next page'

    @pydantic.field_validator('previous_page', mode='after')
    @classmethod
    def replace_previous_page(cls, value):
        # if cls.page_number > 1:
        value = 'previous_page'
        return value
