from fastapi import APIRouter

from .input_models import RegisterUserInputModel

from .operations import create_access_token, create_new_user, signin_user, get_all_users

user_router = APIRouter()


@user_router.post("/signup")
async def signup(user: RegisterUserInputModel):
    db_user = create_new_user(user)
    return db_user


@user_router.post("/signin")
async def signin(username: str, password: str):
    signin_user(username, password)
    # Create jwt token
    token = create_access_token(username)
    return {"access_token": token, "token_type": "jwt token"}
