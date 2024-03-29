"""Authentication commmon functionality"""

from typing import Annotated, Optional

import diskcache
import fastapi
import pydantic
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import common.constants

import configuration
import db.connection
from sqlalchemy import text

CACHE = diskcache.Cache(directory=configuration.CACHE_PATH, disk=diskcache.JSONDisk)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/signin", auto_error=False)

jwt_config = configuration.JwtToken()


def _get_system_user_id_from_db() -> int:
    with db.connection.get_connection() as connection:
        system_user_id = connection.execute(
            text('SELECT ID FROM "Users" WHERE username = :name'), {'name': 'System'}
        ).scalar()
        return system_user_id


def get_system_user_id() -> int:
    """
    Get system user id
    :return:
    """

    system_user_id = CACHE.get('system_user_id')
    if not system_user_id:
        system_user_id = _get_system_user_id_from_db()
        CACHE.set('system_user_id', system_user_id)
        return system_user_id
    return system_user_id


class AuthenticatedUser(pydantic.BaseModel):
    """
    Authenticated users
    """

    id: int
    roles: Optional[list[int]] = None

    @property
    def is_admin(self) -> bool:
        """
        Check if user is admin
        :return:
        """
        return (self.roles and common.constants.ADMIN_ROLE_ID in self.roles) or self.id == get_system_user_id()


async def extract_user_data_from_jwt(
    token: Annotated[str, fastapi.Depends(oauth2_scheme)]
) -> Optional[AuthenticatedUser]:
    """
    Get the current user
    :param token:
    :return:
    """

    if not token:
        return None
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        user_id = int(payload.get("sub"))
        roles = payload.get("roles")
        if user_id is None:
            return None
    except JWTError as e:
        return None
    except ValueError:
        return None

    return AuthenticatedUser(id=user_id, roles=roles)


class Authenticate:
    def __init__(self, optional: bool = False):
        self.optional = optional

    def __call__(
        self,
        user: Annotated[AuthenticatedUser, fastapi.Depends(extract_user_data_from_jwt)],
    ):
        if not self.optional and not user:
            raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
        return user


authenticated_user = Annotated[AuthenticatedUser, fastapi.Depends(Authenticate(optional=False))]
optional_user = Annotated[AuthenticatedUser, fastapi.Depends(Authenticate(optional=True))]


def admin(user: authenticated_user):
    """
    Admin authenticator

    :param user:
    :return:
    """
    if user.is_admin:
        return user
    raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN)
