from fastapi import APIRouter, HTTPException
from db.connection import get_session

from .models import UserOrm
from .input_models import User

from .operations import (create_access_token, check_if_user_exists, get_user_by_username,
                         validate_password, set_password, check_password)

user_router = APIRouter()


@user_router.post("/signup")
async def signup(user: User):
    # Check if the username or email already exists
    db = get_session()
    if check_if_user_exists(db, user.username, user.email):
        # Raise an HTTPException with the error message
        raise HTTPException(
            status_code=409,
            detail="User with this username or email already exists!"
        )

    # Validate password
    try:
        validate_password(user.password)
    except ValueError as e:
        # Raise an HTTPException with the error message
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    # Hash the password
    set_password(user, user.password)

    # Create the user in the database
    with get_session() as session:
        db_user = UserOrm(username=user.username, email=user.email, password=user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


@user_router.post("/signin")
async def signin(username: str, password: str):
    db = get_session()
    # Get user and check if username and password are correct
    current_user = get_user_by_username(db=db, username=username)
    if not current_user or not check_password(current_user, password):
        raise HTTPException(
            status_code=403,
            detail="Incorrect username or password"
        )

    # Create jwt token
    token = create_access_token(username)
    return {"access_token": token, "token_type": "jwt token"}
