from typing import Optional

import pydantic
from pydantic import BaseModel, Field, validator


class PatchIngredientCategoryInputModel(BaseModel):

    """Update ingredient category"""

    field: str
    value: str

class CreateIngredientCategoryInputModel(BaseModel):
    """Create ingredient category"""

    name: str = Field(min_length=3, max_length=255)


class PatchIngredientInputModel(BaseModel):

    """Update ingredient"""

    field: str = Field(max_length=255)
    value: str = Field(max_length=255)


class CreateIngredientInputModel(BaseModel):
    """Create ingredient"""

    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)
    measurement: float = Field(default=0, ge=0)


class UpgradeIngredientInputModel(BaseModel):
    """Update ingredient"""

    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)
    measurement: float = Field(default=0, ge=0)

