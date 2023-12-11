import fastapi
import common.authentication
import common.constants


class AdminOrAuthor:
    """
    Authentication wrapper for Admin or Author
    """
    def __init__(self, identifier_variable: str = None):
        """
        Initialize the authenticator and set identifier field

        :param identifier_variable:
        """
        self.identifier_variable = identifier_variable
