from sqlalchemy import Enum


class TokenTypes(Enum):
    EMAIL_CONFIRMATION = 'email_confirmation'
    PASSWORD_RESET = 'password_reset'


email_subjects = {
    'email_confirmation': 'Email confirmation',
    'password_reset': 'Password reset'
}
