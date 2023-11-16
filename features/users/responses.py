from pydantic import BaseModel


class UsersResponseModel(BaseModel):
    id: int
    username: str
    email: str


class JwtTokenResponseModel(BaseModel):
    token_value: str
    token_type: str


class RolesResponseModel(BaseModel):
    id: int
    name: str


class UserRoleResponseModel(BaseModel):
    user_id: int
    role_id: int
