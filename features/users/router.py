from fastapi import APIRouter

from .input_models import RegisterUserInputModel

from .operations import (create_access_token, create_new_user, signin_user, get_all_users,
                         get_user_by_id_username_email, serialize_users_data, successfully_created_user_response)

user_router = APIRouter()


@user_router.post("/signup")
async def signup(user: RegisterUserInputModel):
    db_user = create_new_user(user)
    serialized_data = serialize_users_data(user=db_user)
    return successfully_created_user_response(serialized_data)


@user_router.post("/signin")
async def signin(username: str, password: str):
    signin_user(username, password)
    # Create jwt token
    token = create_access_token(username)
    return {"access_token": token, "token_type": "jwt token"}


@user_router.get("/all")
async def show_all_users():
    all_users = get_all_users()
    return serialize_users_data(all_users=all_users)


@user_router.get("/user/{user_id}")
async def show_user(user_id: int):
    user = get_user_by_id_username_email(pk=user_id)
    return serialize_users_data(user=user)
