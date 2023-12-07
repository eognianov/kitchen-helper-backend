"""Recipe feature input model"""
from typing import Optional, Union, Any

import fastapi
import pydantic
from sqlalchemy import desc, asc

from features.recipes.models import Recipe, RecipeCategory

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
    page: int = pydantic.Field(default=1)
    page_size: int = pydantic.Field(default=10)
    sorting: Optional[str] = None
    filters: Optional[str] = None
    sort: Optional[list] = []
    filter: Optional[dict] = {}
    order_expression: Optional[list] = []

    @pydantic.field_validator('page', mode='after')
    @classmethod
    def validate_page(cls, field: str):
        if int(field) < 1:
            raise fastapi.HTTPException(status_code=422, detail=f"Page must be greater than 0.")
        return field

    @pydantic.field_validator('page_size', mode='after')
    @classmethod
    def validate_page_size(cls, field: str):
        if int(field) < 1:
            raise fastapi.HTTPException(status_code=422, detail=f"Page size must be greater than 0.")
        return field

    def model_post_init(self, __context: Any) -> None:

        SORTING_FIELDS = ('id', 'name', 'created_by', 'time_to_prepare', 'created_on', 'updated_on',
                          'complexity', 'category.name', 'category.id')

        FILTERING_FIELDS = ('category', 'complexity', 'time_to_prepare', 'created_by', 'period')

        if self.sorting:
            check_sorting = self.sorting.split(',')
            for data in check_sorting:
                data = data.split(':')
                column = data[0]
                direction = data[1] if len(data) > 1 else None

                if column not in SORTING_FIELDS:
                    raise fastapi.HTTPException(status_code=422, detail=f"Invalid sorting column: {column}")

                if direction and direction not in ['asc', 'desc']:
                    raise fastapi.HTTPException(status_code=422, detail=f"Invalid sorting direction: {direction}")

                self.sort.append((column, direction))

                sort_column = getattr(Recipe, column, None)
                if sort_column is None:
                    sort_column = getattr(RecipeCategory, column.split('.')[1], None)

                ordering = desc(sort_column) if direction == 'desc' else asc(sort_column)
                self.order_expression.append(ordering)
        else:
            self.order_expression.append(desc(Recipe.created_on))

        if self.filters:
            for data in self.filters.split(','):
                filter_name = data.split(':')[0]
                conditions = data.split(':')[1] if len(data.split(':')) > 1 else None

                if filter_name not in FILTERING_FIELDS:
                    raise fastapi.HTTPException(status_code=422, detail=f"Invalid filter: {filter_name}")

                if not conditions:
                    raise fastapi.HTTPException(status_code=422, detail=f"Invalid conditions for {filter_name}")

                if filter_name == 'complexity' or filter_name == 'time_to_prepare':
                    conditions = conditions.split('-')
                    try:
                        self.filter[filter_name] = [int(conditions[0]), int(conditions[1])]
                    except (ValueError, IndexError):
                        raise fastapi.HTTPException(status_code=422, detail=f"Invalid range for {filter_name}")

                if filter_name == 'created_by':
                    try:
                        self.filter[filter_name] = int(conditions)
                    except ValueError:
                        raise fastapi.HTTPException(status_code=422,
                                                    detail=f"Invalid input for {filter_name}, must be integer")

                if filter_name == 'period':
                    try:
                        days = int(conditions)
                        if days < 1:
                            raise ValueError
                        self.filter[filter_name] = days
                    except ValueError:
                        raise fastapi.HTTPException(status_code=422, detail=f"Invalid range period")

                if filter_name == 'category':
                    conditions = conditions.split('-')
                    ids = []
                    for category_id in conditions:
                        try:
                            ids.append(int(category_id))
                        except ValueError:
                            raise fastapi.HTTPException(status_code=422, detail=f"Category id must be an integer")
                    self.filter[filter_name] = ids
