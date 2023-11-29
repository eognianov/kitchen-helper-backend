"""Recipe feature input model"""
from typing import Optional

import pydantic


class PatchCategoryInputModel(pydantic.BaseModel):
    """Update category"""

    field: str
    value: str

    @pydantic.field_validator("field")
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = ["NAME"]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        return field


class CreateCategoryInputModel(pydantic.BaseModel):
    """Create category"""

    name: str = pydantic.Field(min_length=3, max_length=255)


class CreateRecipeInputModel(pydantic.BaseModel):
    """Create recipe"""

    name: str = pydantic.Field(max_length=255)
    picture: Optional[str] = pydantic.Field(max_length=255)
    summary: Optional[str] = pydantic.Field(max_length=1000)
    calories: Optional[float] = pydantic.Field(default=0, ge=0)
    carbo: Optional[float] = pydantic.Field(default=0, ge=0)
    fats: Optional[float] = pydantic.Field(default=0, ge=0)
    proteins: Optional[float] = pydantic.Field(default=0, ge=0)
    cholesterol: Optional[float] = pydantic.Field(default=0, ge=0)
    time_to_prepare: int = pydantic.Field(gt=0)
    category_id: Optional[int] = None


class UpgradeRecipeInputModel(pydantic.BaseModel):
    """Update recipe"""

    name: Optional[str] = pydantic.Field(max_length=255)
    picture: Optional[str] = pydantic.Field(max_length=255)
    summary: Optional[str] = pydantic.Field(max_length=1000)
    calories: Optional[float] = pydantic.Field(default=0, ge=0)
    carbo: Optional[float] = pydantic.Field(default=0, ge=0)
    fats: Optional[float] = pydantic.Field(default=0, ge=0)
    proteins: Optional[float] = pydantic.Field(default=0, ge=0)
    cholesterol: Optional[float] = pydantic.Field(default=0, ge=0)
    time_to_prepare: Optional[int] = pydantic.Field(gt=0)
    category_id: Optional[int] = None

    @pydantic.validator("name")
    @classmethod
    def validate_name(cls, name: str):
        if not name:
            raise ValueError("Name is required")

        return name

    @pydantic.validator("time_to_prepare")
    @classmethod
    def validate_time_to_prepare(cls, time_to_prepare: int):
        if not time_to_prepare:
            raise ValueError("Time to prepare is required")

        return time_to_prepare
