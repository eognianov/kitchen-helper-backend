import pydantic

class IngredientCategory(pydantic.BaseModel):

        """Ingredient category model"""

        id: int = pydantic.Field(autoincrement=True, primary_key= True)
        name: str = pydantic.Field(max_length=50)
        created_by: str = pydantic.Field(max_length=30)
        created_on: str = pydantic.Field()
        updated_by: str = pydantic.Field(max_length=30)
        updated_on: str = pydantic.Field()
        ingredients: list["Ingredient"] = pydantic.Field(default=list)


class Ingredient(pydantic.BaseModel):

    id: int = pydantic.Field(autoincrement=True, primary_key= True)
    name: str = pydantic.Field(max_length=255)
    category: str = pydantic.Field(max_length=200)
    calories: float = pydantic.Field(default=0, ge=0)
    carbo: float = pydantic.Field(default=0, ge=0)
    fats: float = pydantic.Field(default=0, ge=0)
    protein: float = pydantic.Field(default=0, ge=0)
    cholesterol: float = pydantic.Field(default=0, ge=0)
    measurement: float = pydantic.Field(default=0, ge=0)