"""Recipe feature input model"""
from typing import Optional, Union, Any

import fastapi
import pydantic

import features.recipes.helpers
from features.recipes import models

INSTRUCTION_CATEGORIES = (
    'WASH AND CHOP',
    'PREHEAT OVEN',
    'SAUTE',
    'BOIL',
    'ROAST',
    'GRILL',
    'STEAM',
    'BAKE',
    'FRY',
    'BLEND',
    'STIR',
    'WHISK',
    'FOLD',
    'KNEAD',
    'SEASONING',
    'PLATING',
    'PRESENTATION',
)


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


class CreateInstructionInputModel(pydantic.BaseModel):
    """Create instruction"""

    instruction: str = pydantic.Field(max_length=300)
    category: str = pydantic.Field(max_length=100)
    time: int = pydantic.Field(ge=1, lt=100)
    complexity: float = pydantic.Field(ge=1, le=5)

    @pydantic.field_validator("category", mode="after")
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

    @pydantic.model_validator(mode="after")
    def check_fields(self) -> "PatchInstructionInputModel":
        allowed_fields_to_edit = ["INSTRUCTION", "CATEGORY", "TIME", "COMPLEXITY"]

        field = self.field
        value = self.value

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        if field.upper() in ["TIME", "COMPLEXITY"]:
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"{field} must be an integer")
            if value < 1:
                raise ValueError(f"{field} must be greater then 1")
            if field.upper() == "TIME" and value > 99:
                raise ValueError(f"Time must be less then 100")
            if field.upper() == "COMPLEXITY" and value > 5:
                raise ValueError(f"Complexity must be less then 6")

        if field.upper() == "CATEGORY":
            if value.upper() not in INSTRUCTION_CATEGORIES:
                raise ValueError(f"{value} is not valid category")

            self.value = self.value.capitalize()

        return self


class PSFRecipesInputModel(pydantic.BaseModel):
    """Paginate, sort, filter Recipes"""

    page: int = pydantic.Field(default=1, gt=0)
    page_size: int = pydantic.Field(default=10, gt=0)
    sort: Optional[str] = None
    filters: Optional[str] = None
    order_expression: Optional[list] = None
    filter_expression: Optional[list] = None

    def model_post_init(self, __context: Any) -> None:
        try:
            self.order_expression = features.recipes.helpers.sort_recipes(self.sort) or []
        except ValueError as ve:
            raise fastapi.HTTPException(status_code=422, detail=str(ve))

        if self.filters:
            try:
                self.filter_expression = features.recipes.helpers.filter_recipes(self.filters) or []
            except ValueError as ve:
                raise fastapi.HTTPException(status_code=422, detail=str(ve))
        else:
            self.filter_expression = []


class IngredientInput(pydantic.BaseModel):
    name: str
    calories: float
    carbo: float
    fats: float
    protein: float
    cholesterol: float
    measurement: str
    category: str

    @staticmethod
    def __positive_field_validator(value, field_name):
        if value < 0:
            raise ValueError(f"{field_name} must be a positive")
        return value

    @pydantic.field_validator("calories", mode="after")
    @classmethod
    def validate_positive_calories(cls, value):
        return cls.__positive_field_validator(value, "calories")

    @pydantic.field_validator("carbo", mode="after")
    @classmethod
    def validate_positive_carbo(cls, value):
        return cls.__positive_field_validator(value, "carbo")

    @pydantic.field_validator("fats", mode="after")
    @classmethod
    def validate_positive_fats(cls, value):
        return cls.__positive_field_validator(value, "fats")

    @pydantic.field_validator("protein", mode="after")
    @classmethod
    def validate_positive_protein(cls, value):
        return cls.__positive_field_validator(value, "protein")

    @pydantic.field_validator("cholesterol", mode="after")
    @classmethod
    def validate_positive_cholesterol(cls, value):
        return cls.__positive_field_validator(value, "cholesterol")

    @pydantic.field_validator("measurement")
    @classmethod
    def validate_measurement(cls, value):
        if value not in [e.value for e in models.IngredientMeasurementEnum]:
            raise ValueError(f"{value} is not a valid measurement")
        return value

    @pydantic.field_validator("category")
    @classmethod
    def validate_category(cls, value):
        if value not in [e.value for e in models.IngredientCategoryEnum]:
            raise ValueError(f"{value} is not a valid category")
        return value
