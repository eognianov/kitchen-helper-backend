from typing import ClassVar, List

from .models import MeasurementUnits
import pydantic
from pydantic import BaseModel, Field, validator


class PatchIngredientCategoryInputModel(BaseModel):

    """Update ingredient category"""

    field: str
    value: str

    # @validator('field')
    # @classmethod
    # def validate_field(cls, field: str):
    #     allowed_fields_to_edit = [
    #         'NAME'
    #     ]
    #
    #     if field.upper() not in allowed_fields_to_edit:
    #         raise ValueError(f'Field {field} is not allowed to be patched')
    #
    #     return field

    @validator('value')
    @classmethod
    def validate_value(cls, value: str):
        if not value:
            raise ValueError('Value cannot be empty')

        return value

class CreateIngredientCategoryInputModel(BaseModel):
    """Create ingredient category"""

    name: str = Field(min_length=3, max_length=255)


class PatchIngredientInputModel(BaseModel):

    """Update ingredient"""

    field: str = Field(max_length=255)
    value: str = Field(max_length=255)
    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)

    # MEASUREMENT_UNITS: ClassVar[list[str]] = [unit.value for unit in MeasurementUnits]
    MEASUREMENT_UNITS: List[str] = [unit.value for unit in MeasurementUnits]

    measurement: str = Field(default=0, ge=0, enum=MEASUREMENT_UNITS)

    class Config:
        allow_mutation = False

    # @validator('field')
    # @classmethod
    # def validate_field(cls, field: str):
    #     allowed_fields_to_edit = [
    #         'NAME',
    #         'MEASUREMENT',
    #         'CALORIES',
    #         'CARBO',
    #         'FATS',
    #         'PROTEINS',
    #         'CHOLESTEROL'
    #     ]
    #
    #     if field.upper() not in allowed_fields_to_edit:
    #         raise ValueError(f'Field {field} is not allowed to be patched')
    #
    #     return field

    @validator('value')
    @classmethod
    def validate_value(cls, value: str):
        if not value:
            raise ValueError('Value cannot be empty')

        return value

    @validator('measurement')
    @classmethod
    def validate_measurement(cls, measurement: str):
        if measurement not in cls.MEASUREMENT_UNITS:
            raise ValueError(f'Measurement {measurement} is not allowed')

        return measurement

class CreateIngredientInputModel(BaseModel):
    """Create ingredient"""

    name: str = Field(min_length=3, max_length=255)
    category: str = Field(max_length=255)
    calories: float = Field(default=0, ge=0)
    carbo: float = Field(default=0, ge=0)
    fats: float = Field(default=0, ge=0)
    proteins: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)

    MEASUREMENT_UNITS = [unit.value for unit in MeasurementUnits]
    measurement: str = Field(default=0, ge=0, enum=MEASUREMENT_UNITS)


    @validator('name')
    @classmethod
    def validate_name(cls, name: str):
        if not name:
            raise ValueError('Name cannot be empty')

        return name

    @validator('measurement')
    @classmethod
    def validate_measurement(cls, measurement: str):
        if measurement not in cls.MEASUREMENT_UNITS:
            raise ValueError(f'Measurement {measurement} is not allowed')

        return measurement