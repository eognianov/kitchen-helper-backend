from pydantic import BaseModel


class UsersResponseModel(BaseModel):
    id: int
    username: str
    email: str
