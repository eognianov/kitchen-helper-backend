from sqlalchemy import Enum


class TokenTypes(Enum):
    EMAIL_CONFIRMATION = 'email_confirmation'
    PASSWORD_RESET = 'password_reset'


class EmailDetails(Enum):
    EMAIL_CONFIRMATION_SUBJECT = 'Email confirmation'
    EMAIL_CONFIRMATION_CONTENT = 'Hello, {}' \
                                 'Thank you for registering!\n\n Please click the link below to confirm your email:' \
                                 '\n{}:{}/users/confirm-email/{}'

    PASSWORD_RESET_SUBJECT = 'Password reset'
    PASSWORD_RESET_CONTENT = 'Hello {},\n\nWe received a request to reset your password. ' \
                             'Please click the link below to reset your password:\n\n' \
                             '{}:{}/users/reset-password/{}\n\nIf you did not request a password reset, ' \
                             'please ignore this email.' \
                             '\n\nThank you!\nPassword Reset Request'
