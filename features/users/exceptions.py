from fastapi import HTTPException


def custom_exception_response(message: str, error_type: str = "") -> list:
    return [{"loc": ["string", 0], "msg": message, "type": error_type}]


class UserDoesNotExistException(Exception):
    ...


class UserAlreadyExists(Exception):
    ...


class AccessDenied(Exception):
    ...
