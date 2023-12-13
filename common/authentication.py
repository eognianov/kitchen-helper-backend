"""Authentication commmon functionality"""

from typing import Annotated, Optional

import fastapi
import pydantic
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

import configuration

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin", auto_error=False)

jwt_config = configuration.JwtToken()


class AuthenticatedUser(pydantic.BaseModel):
    id: int
    roles: list[int]


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
        payload = jwt.decode(
            token, jwt_config.secret_key, algorithms=[jwt_config.algorithm]
        )
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
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED
            )
        return user


authenticated_user = Annotated[
    AuthenticatedUser, fastapi.Depends(Authenticate(optional=False))
]
optional_user = Annotated[
    AuthenticatedUser, fastapi.Depends(Authenticate(optional=True))
]
