"""Recipe feature input model"""
import pydantic


class UpdateCategoryInputModel(pydantic.BaseModel):
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
    name: str = pydantic.Field(min_length=3, max_length=255)