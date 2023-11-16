class UserDoesNotExistException(Exception):
    ...


class UserAlreadyExists(Exception):
    ...


class AccessDenied(Exception):
    ...


class RoleAlreadyExists(Exception):
    ...


class RoleDoesNotExistException(Exception):
    ...
