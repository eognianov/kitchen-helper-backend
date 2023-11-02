"""Here we are having only input models with their validations"""

import pydantic

class CreateUserInputModel(pydantic.BaseModel):
    username: str = pydantic.Field()
    password: str = pydantic.Field()

    @pydantic.field_validator('username')
    def validate_username(self):
        pass

    @pydantic.field_validator('password')
    def validate_password(self):
        """
        We can have different validators depending of the context PROD or DEV
        :return:
        """
        pass