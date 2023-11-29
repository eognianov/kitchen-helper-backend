"""Users feature endpoints"""

import fastapi
from fastapi import APIRouter, HTTPException

import features.users.exceptions
from .constants import TokenTypes
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


@roles_router.get('/')
def get_all_roles(include_users: bool = False):
    """
    Show all roles

    :param include_users:
    :return:
    """
    roles = features.users.operations.get_all_roles()

    if include_users:
        return [RolesWithUsersResponseModel(**role.__dict__) for role in roles]

    return [RolesResponseModel(**role.__dict__) for role in roles]


@roles_router.get('/{role_id}', response_model=RolesWithUsersResponseModel)
def get_role_with_users(role_id: int):
    role = features.users.operations.get_role(role_id)
    return role


@roles_router.post('/', status_code=fastapi.status.HTTP_201_CREATED, response_model=RolesResponseModel)
def create_role(role_request: CreateUserRole):
    """
        Create role

        :param role_request:
        :return:
    """
    try:
        role = features.users.operations.create_role(role_request.name)
    except features.users.exceptions.RoleAlreadyExists:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail=f"Role already exist"
        )

    return role


@user_router.post('/{user_id}/roles/{role_id}', status_code=fastapi.status.HTTP_201_CREATED)
def add_user_to_role(user_id: int, role_id: int):
    """
        Add role to user

        :param user_id:
        :param role_id:
        :return:
    """

    try:
        features.users.operations.add_user_to_role(user_id, role_id)
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
    except features.users.exceptions.UserWithRoleExist:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"User already have this role"
        )


@user_router.delete('/{user_id}/roles/{role_id}', status_code=fastapi.status.HTTP_204_NO_CONTENT)
def remove_user_from_role(user_id: int, role_id: int):
    """
        Remove user from role

        :param user_id:
        :param role_id:
        :return:
    """

    try:
        features.users.operations.remove_user_from_role(user_id, role_id)
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


@user_router.get("/confirm-email/{token}")
async def confirm_email(token: str):
    """
    Confirm email

    :param token:
    :return:
    """

    confirm_token = features.users.operations.check_if_token_is_valid(token=token)
    if confirm_token is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    features.users.operations.confirm_email(confirm_token)

    return fastapi.status.HTTP_200_OK


@user_router.post("/request-password-reset")
async def request_password_reset(email: str):
    """
    Request password reset

    :param email:
    :return:
    """

    db_user = get_user_from_db(email=email)
    if db_user:
        features.users.operations.generate_email_password_token(db_user, TokenTypes.PASSWORD_RESET)

        return fastapi.status.HTTP_200_OK
    else:
        raise HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found")


@user_router.post("/reset-password/{token}")
async def reset_password(token: str, new_password: str):
    """
    Reset password

    :param token:
    :param new_password:
    :return:
    """

    reset_token = features.users.operations.check_if_token_is_valid(token=token)

    if reset_token is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    try:
        user = get_user_from_db(pk=reset_token.user_id)
        features.users.operations.update_user_password(user, new_password)

    except ValueError as e:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.args
        )

    except features.users.exceptions.UserDoesNotExistException:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    except features.users.exceptions.SamePasswordsException:
        raise HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="The new password can not be the same as the old password"
        )

    return fastapi.status.HTTP_200_OK
