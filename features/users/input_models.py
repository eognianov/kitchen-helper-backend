from pydantic import BaseModel, constr, EmailStr


class User(BaseModel):
    # id: int
    username: constr(min_length=3, max_length=30)
    email: EmailStr  # EmailStr for email validation
    password: constr(min_length=8)

