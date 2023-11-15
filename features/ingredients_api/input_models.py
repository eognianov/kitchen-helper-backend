from typing import Optional

import pydantic
from pydantic import BaseModel, Field, validator


class PatchIngredientCategoryInputModel(BaseModel):

    """Update ingredient category"""

    field: str
    value: str

    @pydantic.validator('field')
    @validator('field')
    def validate_field(cls, field: str):

        allowed_fields_to_edit = [
            'NAME'
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        raise field

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

    name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=255)
    calories:Optional[float] = Field(None, ge=0)
    carbo:Optional[float] = Field(None, ge=0)
    fats:Optional[float] = Field(None, ge=0)
    proteins:Optional[float] = Field(None, ge=0)
    cholesterol:Optional[float] = Field(None, ge=0)
    measurement:Optional[float] = Field(None, ge=0)

    @validator('name')
    def validate_name(cls, name):
        if name is not None and len(name) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return name