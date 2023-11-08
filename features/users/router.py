"""Users feature endpoints"""
from typing import List

import fastapi
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

import features.users.exceptions
from .input_models import RegisterUserInputModel, UpdateUserInputModel
from .responses import UsersResponseModel

from .operations import create_token, create_new_user, signin_user, get_all_users, get_user

user_router = APIRouter()


@user_router.post("/signup")
async def signup(user: RegisterUserInputModel):
    """
    Sing up user

    :param user:
    :return:
    """
    try:
        db_user = create_new_user(user)
        return JSONResponse(
            content={
                "message": "Successfully created",
                "user_data": {"id": db_user.id, "username": db_user.username, "email": db_user.email}
            },
            status_code=201
        )
    except features.users.exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail=features.users.exceptions.custom_exception_response(
                message="User with this username or email already exists!"
            )
        )


@user_router.post("/signin")
async def signin(username: str, password: str):
    """
    Sing in user

    :param username:
    :param password:
    :return:
    """
    try:
        signin_user(username, password)
        # Create jwt token
        token, token_type = create_token(username)
        return {"token": token, "token_type": token_type}
    except features.users.exceptions.AccessDenied:
        raise HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail=features.users.exceptions.custom_exception_response(message="Incorrect username or password")
        )


@user_router.get("/all", response_model=List[UsersResponseModel])
async def show_all_users():
    """
    Show all users

    :return:
    """
    all_users = get_all_users()
    return all_users


@user_router.get("/{user_id}", response_model=UsersResponseModel)
async def show_user(user_id: int):
    """
    Show user details

    :param user_id:
    :return:
    """
    try:
        user = get_user(pk=user_id)
        return user
    except features.users.exceptions.UserDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User with id <{user_id}> does not exist"
        )


@user_router.patch('/{user_id}')
def update_user(user_id: int = fastapi.Path(), update_user_input_model: UpdateUserInputModel = fastapi.Body()):
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
