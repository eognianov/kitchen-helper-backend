"""Recipe feature input model"""
from typing import Optional, Union, Any

import fastapi
import pydantic

import features.recipes.helpers
from features.recipes import constants

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
    time: int = pydantic.Field(ge=1)
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
    name: str = pydantic.Field(max_length=100, min_length=3)
    calories: float = pydantic.Field(ge=0)
    carbo: float = pydantic.Field(ge=0)
    fats: float = pydantic.Field(ge=0)
    protein: float = pydantic.Field(ge=0)
    cholesterol: float = pydantic.Field(ge=0)
    measurement: str
    category: str

    @pydantic.field_validator("measurement")
    @classmethod
    def validate_measurement(cls, value):
        if value.upper() not in constants.INGREDIENT_MEASUREMENT_UNITS:
            raise ValueError(f"{value} is not a valid measurement")
        return value

    @pydantic.field_validator("category")
    @classmethod
    def validate_category(cls, value):
        if value.upper() not in constants.INGREDIENT_CATEGORIES:
            raise ValueError(f"{value} is not a valid category")
        return value


class UpdateIngredientInputModel(pydantic.BaseModel):
    """Update Ingredient Input Model"""

    field: str
    value: str

    @pydantic.model_validator(mode="after")
    def validate_field(self):
        allowed_fields = {
            'NAME': lambda value: self.__validate_name(value),
            'CALORIES': lambda value: self.__validate_numeric(value),
            'CARBO': lambda value: self.__validate_numeric(value),
            'FATS': lambda value: self.__validate_numeric(value),
            'PROTEIN': lambda value: self.__validate_numeric(value),
            'CHOLESTEROL': lambda value: self.__validate_numeric(value),
            'MEASUREMENT': lambda value: self.__validate_measurement(value),
            'CATEGORY': lambda value: self.__validate_category(value),
        }

        if self.field.upper() not in allowed_fields:
            raise ValueError(f"You are not allowed to edit {self.field} field")

        allowed_fields[self.field.upper()](self.value)
        return self

    @staticmethod
    def __validate_name(value):
        if not (3 <= len(value) <= 100):
            raise ValueError("Name must be between 3 and 100 characters")
        return value

    @staticmethod
    def __validate_numeric(value):
        try:
            float(value)
            if float(value) < 0:
                raise ValueError
        except ValueError:
            raise ValueError("Value must be a positive number")
        return value

    @staticmethod
    def __validate_measurement(value):
        if value.upper() not in constants.INGREDIENT_MEASUREMENT_UNITS:
            raise ValueError(f"{value} is not a valid measurement")
        return value

    @staticmethod
    def __validate_category(value):
        if value.upper() not in constants.INGREDIENT_CATEGORIES:
            raise ValueError(f"{value} is not a valid category")
        return value


class PatchRecipeInputModel(pydantic.BaseModel):
    """Update category"""

    field: str
    value: str | int | bool

    @pydantic.field_validator("field")
    @classmethod
    def validate_field(cls, field: str):
        allowed_fields_to_edit = [
            "NAME",
            'PICTURE',
            'SUMMARY',
            'TIME_TO_PREPARE',
            'CATEGORY_ID',
            'IS_PUBLISHED',
        ]

        if field.upper() not in allowed_fields_to_edit:
            raise ValueError(f"You are not allowed to edit {field} column")

        return field

    @pydantic.model_validator(mode='after')
    def validate_model(self):
        def __validate_string_length(*, field: str, value: str, max_length: int, min_length: int = 3):
            """Validate string length"""
            if not (min_length <= len(value) <= max_length):
                raise ValueError(f'The length of {field} must be in the range [{min_length}, {max_length}]!')

        def __validate_integer_size(*, field: str, value: str, min_value: int = 0, max_value: int | None = None):
            """Validate integer"""
            try:
                parsed_value = int(value)
            except ValueError:
                raise ValueError(f'You must provide valid integer for {field}')
            is_valid = parsed_value >= min_value
            if max_value:
                is_valid = is_valid and parsed_value <= max_value
            if not is_valid:
                raise ValueError(f"{field} value must be > {min_value} {f'and < {max_value}' if max_value else ''}!")

        def __validate_bool(*, field: str, value: str):
            try:
                bool(value)
            except:
                raise ValueError(f"{field} value must be a valid boolean")

        def _validate_name(*, field: str, value: str):
            return __validate_string_length(field=field, value=value, max_length=255)

        def _validate_positive_integer(*, field: str, value: str):
            return __validate_integer_size(field=field, value=value, min_value=1)

        def _validate_summary(*, field: str, value: str):
            return __validate_string_length(field=field, value=value, min_length=3, max_length=1000)

        def validate_is_published(*, field: str, value: str):
            return __validate_bool(field=field, value=value)

        validators = {
            'NAME': [_validate_name],
            'PICTURE': [_validate_positive_integer],
            'SUMMARY': [_validate_summary],
            'TIME_TO_PREPARE': [_validate_positive_integer],
            'CATEGORY_ID': [_validate_positive_integer],
            'IS_PUBLISHED': [validate_is_published],
        }

        validator_functions = validators.get(self.field.upper(), [])
        for validator in validator_functions:
            validator(field=self.field, value=self.value)

        return self

    def model_post_init(self, __context: Any) -> None:
        """
        Parse the value after init
        :param __context:
        :return:
        """

        def _parse_bool(value: str) -> bool:
            if value.isdigit():
                return bool(value)
            elif value.isalpha() and value.casefold() in ['true', 'false']:
                return eval(value.capitalize())
            return False

        parsers = {'PICTURE': int, 'TIME_TO_PREPARE': int, 'CATEGORY_ID': int, 'IS_PUBLISHED': _parse_bool}

        self.value = parsers.get(self.field.upper(), lambda x: x)(self.value)
