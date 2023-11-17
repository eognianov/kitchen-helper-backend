"""Users feature endpoints"""

import fastapi
from fastapi import APIRouter, HTTPException

import features.users.exceptions
from .input_models import RegisterUserInputModel, UpdateUserInputModel, CreateUserRole
from .operations import create_new_user, signin_user, get_all_users, get_user_from_db
from .responses import UsersResponseModel, JwtTokenResponseModel, RolesResponseModel, RolesWithUsersResponseModel

user_router = APIRouter()
roles_router = APIRouter()


@user_router.post("/signup", response_model=UsersResponseModel)
async def signup(user: RegisterUserInputModel):
    """
    Sing up user

    :param user:
    :return:
    """
    try:
        db_user = create_new_user(user)
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


@roles_router.get('/', response_model=list[RolesResponseModel])
def get_all_roles():
    """
    Show all roles

    :return:
    """
    all_roles = features.users.operations.get_all_roles()
    return all_roles


@roles_router.post('/', status_code=fastapi.status.HTTP_201_CREATED, response_model=RolesResponseModel)
def create_role(role_request: CreateUserRole):
    """
        Create role

        :param role_request:
        :return:
    """
    try:
        role = features.users.operations.get_role(role_name=role_request.name)
        if role:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_409_CONFLICT,
                detail=f"Role already exist"
            )
    except features.users.exceptions.RoleDoesNotExistException:
        role = features.users.operations.create_role(role_request.name)
        return role


@roles_router.post('/{user_id}/{role_id}', status_code=fastapi.status.HTTP_201_CREATED)
def add_role_to_user(user_id: int, role_id: int):
    """
        Add role to user

        :param user_id:
        :param role_id:
        :return:
    """

    try:
        user = features.users.operations.get_user_from_db(pk=user_id)
        role = features.users.operations.get_role(pk=role_id)
        user_role = features.users.operations.check_user_role(user_id, role_id)
        if user_role:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_409_CONFLICT,
                detail=f"User already have this role"
            )
    except features.users.exceptions.UserDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User does not exist"
        )
    except features.users.exceptions.RoleDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Role does not exist"
        )
    except features.users.exceptions.UserWithRoleDoesNotExist:
        features.users.operations.add_role_to_user(user_id, role_id)


@roles_router.delete('/{user_id}/{role_id}', status_code=fastapi.status.HTTP_204_NO_CONTENT)
def remove_role_from_user(user_id: int, role_id: int):
    """
        Remove role from user

        :param user_id:
        :param role_id:
        :return:
    """

    try:
        user = features.users.operations.get_user_from_db(pk=user_id)
        role = features.users.operations.get_role(pk=role_id)
        user_role = features.users.operations.check_user_role(user_id, role_id)
    except features.users.exceptions.UserDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User does not exist"
        )
    except features.users.exceptions.RoleDoesNotExistException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Role does not exist"
        )
    except features.users.exceptions.UserWithRoleDoesNotExist:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"No user with this role"
        )

    features.users.operations.remove_role_from_user(user_id, role_id)


@roles_router.get('/users', response_model=list[RolesWithUsersResponseModel])
def get_all_roles_with_users():
    roles = get_all_roles()
    return roles
