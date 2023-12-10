from .models import MeasurementUnits
from pydantic import BaseModel, Field, field_validator

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


    measurement: str = Field(default=0, ge=0, enum=MEASUREMENT_UNITS)

    class Config:
        allow_mutation = False

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
    def validate_value(cls, value: str):
        if not value:
            raise ValueError('Value cannot be empty')

        return value

    @field_validator('measurement')
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

    measurement: str = Field(default=0, ge=0)

    @field_validator('measurement')
    @classmethod
    def validate_measurement(cls, measurement: str):
        if measurement not in MEASUREMENT_UNITS:
            raise ValueError(f'Measurement {measurement} is not allowed')

        return measurement