"""Users feature endpoints"""

import fastapi
from fastapi import APIRouter, HTTPException

import features.users.exceptions
from .input_models import RegisterUserInputModel, UpdateUserInputModel
from .responses import UsersResponseModel, JwtTokenResponseModel

from .operations import create_new_user, signin_user, get_all_users, get_user_from_db

user_router = APIRouter()


@user_router.post("/signup", response_model=UsersResponseModel)
async def signup(user: RegisterUserInputModel):
    """
    Sing up user

    :param user:
    :return:
    """
    try:
        db_user = create_new_user(user)
        token = features.users.operations.generate_email_confirmation_token(db_user)
        await features.users.operations.send_email(db_user, token)
        return db_user
    except features.users.exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail="User with this username or email already exists!"
        )


@user_router.post("/signin", response_model=JwtTokenResponseModel)
async def signin(username: str, password: str):
    """
    Sing in user

    :param username:
    :param password:
    :return:
    """
    try:
        # Sign in user and create jwt token
        token, token_type = signin_user(username, password)
        return JwtTokenResponseModel(token_value=token, token_type=token_type)
    except features.users.exceptions.AccessDenied:
        raise HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password"
        )


@user_router.get("/all", response_model=list[UsersResponseModel])
async def show_all_users():
    """
    Show all users

    :return:
    """
    all_users = get_all_users()
    return all_users


@user_router.get("/{user_id}", response_model=UsersResponseModel)
async def get_user(user_id: int):
    """
    Show user details

    :param user_id:
    :return:
    """
    try:
        user = get_user_from_db(pk=user_id)
        return user
    except features.users.exceptions.UserDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id=} does not exist"
        )


@user_router.patch('/{user_id}')
def patch_user(user_id: int = fastapi.Path(), update_user_input_model: UpdateUserInputModel = fastapi.Body()):
    """
    Update user email

    :param user_id:
    :param update_user_input_model:
    :return:
    """
    try:
        updated_user = features.users.operations.update_user(user_id, **update_user_input_model.model_dump())
        return features.users.responses.UsersResponseModel(**updated_user.__dict__)
    except features.users.exceptions.UserDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User with {user_id=} does not exist"
        )


@user_router.get("/confirm-email/{token}")
async def confirm_email(token: str):
    """
    Confirm email

    :param token:
    :return:
    """
    token = features.users.operations.get_token_from_db(email_confirmation_token=token)
    if not token:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token"
        )

    user = features.users.operations.confirm_email(token.user_id)

    return {"message": "Email confirmed successfully", "email": user.email}
