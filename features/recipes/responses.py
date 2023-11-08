"""Recipes feature responses"""
import datetime
from typing import Optional, Any
import pydantic


class Category(pydantic.BaseModel):
    """Category response"""
    id: int
    name: str
    created_by: str
    created_on: datetime.datetime
    updated_by: Optional[str] = None
    updated_on: Optional[datetime.datetime] = None


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
    created_by: str
    created_on: datetime.datetime
    updated_by: Optional[str]
    updated_on: datetime.datetime
    category: Category | Any = None

    def model_post_init(self, __context: Any):
        if self.category:
            self.category = Category(**self.category.__dict__)
