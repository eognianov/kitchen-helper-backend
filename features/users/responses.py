"""Users feature responses"""
from pydantic import BaseModel


class UsersResponseModel(BaseModel):
    """User response"""
    id: int
    username: str
    email: str


class JwtTokenResponseModel(BaseModel):
    """JWT Token response"""
    token_value: str
    token_type: str
