from typing import Any

"""Users feature responses"""
from pydantic import BaseModel


class RolesResponseModel(BaseModel):
    id: int
    name: str


class UsersResponseModel(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    roles: list[RolesResponseModel] | Any = None

    def model_post_init(self, __context: Any):
        if self.roles:
            self.roles = [RolesResponseModel(**_.__dict__) for _ in self.roles]


class JwtTokenResponseModel(BaseModel):
    access_token: str
    token_type: str


class UsersResponseModelWithoutRoles(BaseModel):
    id: int
    username: str
    email: str


class RolesWithUsersResponseModel(BaseModel):
    id: int
    name: str
    users: list[UsersResponseModelWithoutRoles] | Any = None

    def model_post_init(self, __context: Any):
        if self.users:
            self.users = [UsersResponseModelWithoutRoles(**_.__dict__) for _ in self.users]
