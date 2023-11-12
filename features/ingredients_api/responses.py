import pydantic


class Ingredient(pydantic.BaseModel):

    id: int
    name: str = pydantic.Field(max_length=255)
    category: str = pydantic.Field(max_length=200)
    calories: float = pydantic.Field(default=0, ge=0)
    carbo: float = pydantic.Field(default=0, ge=0)
    fats: float = pydantic.Field(default=0, ge=0)
    protein: float = pydantic.Field(default=0, ge=0)
    cholesterol: float = pydantic.Field(default=0, ge=0)
    measurement: float = pydantic.Field(default=0, ge=0)