"""Recipe feature input model"""
from typing import Optional, Union

import pydantic
from sqlalchemy import desc, asc

from features.recipes.models import Recipe

INSTRUCTION_CATEGORIES = ('BREAKFAST', 'LUNCH', 'DINNER')


class PatchCategoryInputModel(pydantic.BaseModel):
    """Update category"""

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


class CreateCategoryInputModel(pydantic.BaseModel):
    """Create category"""

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


class PaginateRecipiesInputModel(pydantic.BaseModel):
    """Paginate Recipes"""
    page: Optional[int] = pydantic.Field(gt=0, default=1)
    page_size: Optional[int] = pydantic.Field(gt=0, default=10)
    sorting: Optional[str] = None
    filters: Optional[str] = None

    @pydantic.field_validator('sorting', mode='after')
    @classmethod
    def validate_sorting(cls, field: str):
        order_expression = []
        if field:
            sorting = field.split(',')
            for data in sorting:
                data = data.split('-')
                sort_column = data[0]
                direction = data[1] if len(data) > 1 else None

                if direction and direction.lower() not in ['asc', 'desc']:
                    raise ValueError(f"Invalid sorting direction for {sort_column} column")

                column = getattr(Recipe, sort_column, None)
                ordering = desc(column) if direction == 'desc' else asc(column)
                order_expression.append(ordering)
            else:
                order_expression.append(asc(Recipe.id))
        return order_expression

    @pydantic.field_validator('filters', mode='after')
    @classmethod
    def validate_filters(cls, field: str):
        if field:
            return field.upper()
