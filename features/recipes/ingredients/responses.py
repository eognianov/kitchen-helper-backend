import pydantic
from features.recipes.ingredients.models import Ingredient


class IngredientCategory(pydantic.BaseModel):

    """Ingredient category model"""

    id: int = pydantic.Field(autoincrement=True, primary_key=True)
    name: str = pydantic.Field(max_length=50)
    created_by: str = pydantic.Field(max_length=30)
    created_on: str = pydantic.Field()
    updated_by: str = pydantic.Field(max_length=30)
    updated_on: str = pydantic.Field()
    ingredients: list["Ingredient"] = pydantic.Field(default=list)
