import fastapi
import common.authentication
import common.constants


class AdminOrMe:
    """
    Authentication wrapper for Admin or Me
    """
    def __init__(self, identifier_variable: str = None):
        """
        Initialize the authenticator and set identifier field

        :param identifier_variable:
        """
        self.identifier_variable = identifier_variable

    def __call__(self, user: common.authentication.authenticated_user, request: fastapi.Request):
        """
        Actual authentication

        :param user:
        :param request:
        :return:
        """
        if int(request.path_params.get(self.identifier_variable)) == user.id or common.constants.ADMIN_ROLE_ID in user.roles:
            return user
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
