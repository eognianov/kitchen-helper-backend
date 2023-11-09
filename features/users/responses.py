from pydantic import BaseModel


class UsersResponseModel(BaseModel):
    id: int
    username: str
    email: str


class JwtTokenResponseModel(BaseModel):
    token_value: str
    token_type: str
