from fastapi import APIRouter

from .input_models import RegisterUserInputModel, UsersResponseModel

from .operations import create_access_token, create_new_user, signin_user, get_all_users, get_user_by_id_username_email, \
    serialize_users_data

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


@user_router.get("/all")
async def show_all_users():
    all_users = get_all_users()
    return serialize_users_data(all_users)


@user_router.get("/user/{user_id}", response_model=UsersResponseModel)
async def show_user(user_id: int):
    return get_user_by_id_username_email(pk=user_id)
