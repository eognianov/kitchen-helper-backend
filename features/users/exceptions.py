"""Users feature exceptions"""


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


class UserWithRoleDoesNotExist(Exception):
    ...


class UserWithRoleExist(Exception):
    ...


class SamePasswordsException(Exception):
    ...


class FailedToSendEmailException(Exception):
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
