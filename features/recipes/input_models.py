"""Recipe feature input model"""
from typing import Optional, Union
from .models import MeasurementUnits
from pydantic import BaseModel, Field, field_validator

import pydantic

INSTRUCTION_CATEGORIES = ('BREAKFAST', 'LUNCH', 'DINNER')

MEASUREMENT_UNITS = [unit.value for unit in MeasurementUnits]


class PatchIngredientCategoryInputModel(BaseModel):

    """Update ingredient category"""

    field: str
    value: str

    @field_validator('field')
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = [
            'NAME'
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f'Field {field} is not allowed to be patched')

        return field

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: str):
        if not value:
            raise ValueError('Value cannot be empty')

        return value


class CreateIngredientCategoryInputModel(BaseModel):
    """Create ingredient category"""

    name: str = Field(min_length=3, max_length=255)


class UpdateIngredientInputModel(BaseModel):

    """Update ingredient"""

    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)
    measurement: str = Field(default=0, ge=0, enum=MEASUREMENT_UNITS)

    class Config:
        allow_mutation = False


    @field_validator('measurement')
    @classmethod
    def validate_measurement(cls, measurement: str):
        if measurement not in cls.MEASUREMENT_UNITS:
            raise ValueError(f'Measurement {measurement} is not allowed')

        return measurement


class PatchIngredientInputModel(BaseModel):

    """Patch ingredient"""

    field: str
    value: Union[str, float, int]

    @field_validator('field')
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = [
            'NAME',
            'MEASUREMENT',
            'CALORIES',
            'CARBO',
            'FATS',
            'PROTEINS',
            'CHOLESTEROL'
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f'Field {field} is not allowed to be patched')

        return field

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: Union[str, float, int]):
        if not value:
            raise ValueError('Value cannot be empty')

        return value


class CreateIngredientInputModel(BaseModel):
    """Create ingredient"""

    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)

    measurement: str = Field(required=True, enum=MEASUREMENT_UNITS)

    @field_validator('measurement')
    @classmethod
    def validate_measurement(cls, measurement: str):
        if measurement not in MEASUREMENT_UNITS:
            raise ValueError(f'Measurement {measurement} is not allowed')

        return measurement


class RecipesPatchCategoryInputModel(pydantic.BaseModel):
    """Update recipes category"""

    field: str
    value: str

    @pydantic.field_validator('field')
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = [
            'NAME'
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        return field


class CreateRecipesCategoryInputModel(pydantic.BaseModel):
    """Create recipes category"""

    name: str = pydantic.Field(min_length=3, max_length=255)


class CreateInstructionInputModel(pydantic.BaseModel):
    """Create instruction"""
    instruction: str = pydantic.Field(max_length=300)
    category: str = pydantic.Field(max_length=100)
    time: int = pydantic.Field(ge=1, lt=100)
    complexity: float = pydantic.Field(ge=1, le=5)

    @pydantic.field_validator('category', mode='after')
    @classmethod
    def validate_category(cls, field: str):
        if field.upper() not in INSTRUCTION_CATEGORIES:
            raise ValueError(f"{field} is not valid category")
        return field.capitalize()


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
    instructions: Optional[list[CreateInstructionInputModel]] = None


class PatchInstructionInputModel(pydantic.BaseModel):
    """Update instruction"""

    field: str
    value: Union[str, int]

    @pydantic.model_validator(mode='after')
    def check_fields(self) -> 'PatchInstructionInputModel':
        allowed_fields_to_edit = [
            'INSTRUCTION', 'CATEGORY', 'TIME', 'COMPLEXITY'
        ]

        field = self.field
        value = self.value

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        if field.upper() in ['TIME', 'COMPLEXITY']:
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"{field} must be an integer")
            if value < 1:
                raise ValueError(f"{field} must be greater then 1")
            if field.upper() == 'TIME' and value > 99:
                raise ValueError(f"Time must be less then 100")
            if field.upper() == 'COMPLEXITY' and value > 5:
                raise ValueError(f"Complexity must be less then 6")

        if field.upper() == 'CATEGORY':
            if value.upper() not in INSTRUCTION_CATEGORIES:
                raise ValueError(f"{value} is not valid category")

            self.value = self.value.capitalize()

        return self
