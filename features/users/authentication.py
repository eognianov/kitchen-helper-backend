import fastapi
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
import configuration
from .operations import get_user_from_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin")

config = configuration.Config()


async def get_current_user(token: Annotated[str, fastapi.Depends(oauth2_scheme)]):
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.jwt.secret_key, algorithms=[config.jwt.algorithm])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception
    user = get_user_from_db(pk=user_id)
    if user is None:
        raise credentials_exception
    return user