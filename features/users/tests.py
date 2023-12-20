import datetime

import bcrypt
import pytest

from unittest.mock import patch, AsyncMock, ANY

import configuration
import db.connection
from tests.fixtures import use_test_db
from features.users import operations, input_models, exceptions, constants, models
from fastapi.testclient import TestClient
from api import app

USER_DATA = {
    "username": "test_user",
    "email": "test@mail.com",
    "password": "Password1@",
}

ROLE_DATA = {"name": "admin"}

config = configuration.Config()


class TestUserOperations:
    """
    Tests for user operations
    """

    @staticmethod
    def test_hashed_password_matches_expected(use_test_db):
        """
        Test that hashed password
        :param use_test_db:
        :return:
        """
        password = "secure_password"
        hashed_password = operations._hash_password(password=password)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed_password) is True

    @staticmethod
    def test_check_password_expected_true(use_test_db):
        """
        Test that password is equal to user's hashed password
        :param use_test_db:
        :return:
        """
        assert (
            operations.check_password(
                operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA)),
                USER_DATA["password"],
            )
            is True
        )

    @staticmethod
    def test_check_password_expected_false(use_test_db):
        """
        Test that password is different from user's hashed password
        :param use_test_db:
        :return:
        """
        different_password = "different password"
        assert (
            operations.check_password(
                user=operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA)),
                password=different_password,
            )
            is False
        )

    @staticmethod
    def test_create_new_user_without_role_success(use_test_db):
        """
        Test that creating user without role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        assert user.username == USER_DATA["username"]
        assert user.email == USER_DATA["email"]
        assert user.id == 1
        assert user.roles == []

    @staticmethod
    def test_create_new_user_with_roles_success(use_test_db):
        """
        Test that creating user with role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        updated_user = operations.get_user_from_db(pk=user.id)

        assert updated_user.username == USER_DATA["username"]
        assert updated_user.email == USER_DATA["email"]
        assert updated_user.id == 1
        assert len(updated_user.roles) == 1
        assert updated_user.roles[0] == role

    @staticmethod
    def test_signin_user_expected_success(use_test_db):
        """
        Test that signin user is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        assert operations.signin_user(username=USER_DATA["username"], password=USER_DATA["password"]) == user

    @staticmethod
    def test_signin_user_not_existing_username_expected_exception(use_test_db):
        """
        Test that signin user with not existing username is not successful
        :param use_test_db:
        :return:
        """
        different_username = "different_username"
        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.signin_user(username=different_username, password=USER_DATA["password"])

    @staticmethod
    def test_signin_user_wrong_password_expected_exception(use_test_db):
        """
        Test that signin user with wrong password is not successful
        :param use_test_db:
        :return:
        """
        wrong_password = "wrong_password"
        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        with pytest.raises(exceptions.AccessDenied):
            operations.signin_user(USER_DATA["username"], wrong_password)

    @staticmethod
    def test_get_user_from_db_with_pk_expected_success(use_test_db):
        """
        Test get user from database with pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        assert operations.get_user_from_db(pk=user.id) == user

    @staticmethod
    def test_get_user_from_db_with_wrong_pk_expected_exception(use_test_db):
        """
        Test get user from database with wrong pk
        :param use_test_db:
        :return:
        """
        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(pk=2)

    @staticmethod
    def test_get_user_from_db_with_username_expected_success(use_test_db):
        """
        Test get user from database with username
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**USER_DATA))
        assert operations.get_user_from_db(username=user.username) == user

    @staticmethod
    def test_get_user_from_db_with_wrong_username_expected_exception(use_test_db):
        """
        Test get user from database with wrong username
        :param use_test_db:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**USER_DATA))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(username="wrong_username")

    @staticmethod
    def test_get_user_from_db_with_email_expected_success(use_test_db):
        """
        Test get user from database with email
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**USER_DATA))
        assert operations.get_user_from_db(email=user.email) == user

    @staticmethod
    def test_get_user_from_db_with_wrong_email_expected_exception(use_test_db):
        """
        Test get user from database with wrong email
        :param use_test_db:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**USER_DATA))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(email="wrong_email@test.com")

    @staticmethod
    def test_get_all_users_no_users_in_database_expected_empty_list(use_test_db):
        """
        Test get all users from database without users in the database
        :param use_test_db:
        :return:
        """
        all_users = operations.get_all_users()
        assert all_users == []
        assert len(all_users) == 0

    @staticmethod
    def test_get_all_users_one_user_in_database_expected_list_with_one_user(use_test_db):
        """
        Test get all users from database with one user in the database
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**USER_DATA))
        all_users = operations.get_all_users()
        assert all_users[0] == user
        assert len(all_users) == 1

    @staticmethod
    def test_get_all_users_more_users_in_database_expected_list_with_same_users(use_test_db):
        """
        Test get all users from database with more users in the database
        :param use_test_db:
        :return:
        """
        total_users = 5
        users = []
        for i in range(total_users):
            users.append(
                operations.create_new_user(
                    user=input_models.RegisterUserInputModel(
                        username=f"{USER_DATA['username']}{i}",
                        email=f"{i}{USER_DATA['email']}",
                        password=USER_DATA["password"],
                    )
                )
            )
        all_users = operations.get_all_users()
        assert all_users[0] == users[0]
        assert all_users[-1] == users[-1]
        assert len(all_users) == total_users

    @staticmethod
    def test_update_user_expected_user_to_be_updated(use_test_db):
        """
        Test update user with expected user data
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        new_email = "updated@tets.com"
        updated_user = operations.update_user(user_id=user.id, field="email", value=new_email, updated_by=user.id)
        assert updated_user.email == new_email

    @staticmethod
    def test_create_token_expected_bearer_token_type(use_test_db):
        """
        Test create token with expected token type (access token) to be created
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        _, token_type = operations.create_token(user_id=user.id)
        assert token_type == "Bearer"

    @staticmethod
    def test_create_token_expected_refresh_token_type(use_test_db):
        """
        Test create token with expected token type (refresh token) to be created
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        _, token_type = operations.create_token(user_id=user.id, access=False)
        assert token_type == "Refresh"

    @staticmethod
    def test_get_all_roles_no_roles_in_database_expected_empty_list(use_test_db):
        """
        Test get all roles from database without roles in the database
        :param use_test_db:
        :return:
        """
        all_roles = operations.get_all_roles()
        assert all_roles == []
        assert len(all_roles) == 0

    @staticmethod
    def test_get_all_roles_one_role_in_database_expected_list_with_one_role(use_test_db):
        """
        Test get all roles from database with one role in the database
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        all_roles = operations.get_all_roles()
        assert all_roles[0] == role
        assert len(all_roles) == 1
        assert all_roles[0].name == role.name
        assert all_roles[0].created_by == user.id

    @staticmethod
    def test_get_all_roles_more_roles_in_database_expected_list_with_same_len(use_test_db):
        """
        Test get all roles from database with three role in the database
        :param use_test_db:
        :return:
        """
        number_of_roles = 3
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        roles = []
        for i in range(number_of_roles):
            roles.append(operations.create_role(name=f"{ROLE_DATA['name']}{i}", created_by=user.id))

        all_roles = operations.get_all_roles()
        assert all_roles[0] == roles[0]
        assert all_roles[-1] == roles[-1]
        assert len(all_roles) == number_of_roles
        assert all_roles[0].name == roles[0].name
        for role in all_roles:
            assert role.created_by == user.id

    @staticmethod
    def test_get_role_with_pk_expected_success(use_test_db):
        """
        Test get role from database with pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        assert operations.get_role(pk=role.id) == role

    @staticmethod
    def test_get_role_with_wrong_pk_expected_exception(use_test_db):
        """
        Test get role from database with wrong pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(pk=2)

    @staticmethod
    def test_get_role_with_name_expected_success(use_test_db):
        """
        Test get role from database with role name
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        assert operations.get_role(role_name=role.name) == role

    @staticmethod
    def test_get_role_with_wrong_name_expected_exception(use_test_db):
        """
        Test get role from database with wrong name
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(role_name="wrong_name")

    @staticmethod
    def test_get_role_without_params_expected_exception(use_test_db):
        try:
            operations.get_role()
        except ValueError as e:
            assert "Neither pk nor role_name is provided" in str(e)

    @staticmethod
    def test_check_user_role_expected_true(use_test_db):
        """
        Test check user role expected role to be in user's roles
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is True

    @staticmethod
    def test_check_user_role_expected_false(use_test_db):
        """
        Test check user role expected role not to be in user's roles
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is False

    @staticmethod
    def test_create_role_expected_success(use_test_db):
        """
        Test that creating role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        assert role.name == ROLE_DATA["name"]
        assert role.created_by == user.id
        assert role.id == 1

    @staticmethod
    def test_create_same_role_expected_exception(use_test_db):
        """
        Test that creating same role will raise exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleAlreadyExists):
            operations.create_role(ROLE_DATA["name"], created_by=user.id)

    @staticmethod
    def test_add_user_to_role_expected_success(use_test_db):
        """
        Test adding user to role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(ROLE_DATA["name"], created_by=user.id)
        user_roles = user.roles
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        db_user = operations.get_user_from_db(pk=user.id)

        assert db_user.roles[0] == role
        assert len(db_user.roles) == len(user_roles) + 1
        assert db_user.roles == [role]

    @staticmethod
    def test_add_user_to_role_user_already_added_expected_exception(use_test_db):
        """
        Test adding user to role when already added raise exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        with pytest.raises(exceptions.UserWithRoleExist):
            operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)

    @staticmethod
    def test_remove_user_from_role_user_not_added_expected_exception(use_test_db):
        """
        Test removing user from role when not added raise exception expected
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name=ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.UserWithRoleDoesNotExist):
            operations.remove_user_from_role(role_id=role.id, user_id=user.id, removed_by=user.id)

    @staticmethod
    def test_remove_user_from_role_when_user_is_added_expected_success(use_test_db):
        """
        Test removing user from role when added expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        user_roles = operations.get_user_from_db(pk=user.id).roles
        operations.remove_user_from_role(user_id=user.id, role_id=role.id, removed_by=user.id)
        db_user = operations.get_user_from_db(pk=user.id)

        assert db_user.roles != user_roles
        assert len(db_user.roles) == len(user_roles) - 1
        assert db_user.roles == []

    @staticmethod
    def test_prepare_mail_template_email_confirmation_expected_success(use_test_db):
        """
        Test that the email template include the correct url
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION)
        confirmation_link = f"{config.server.host}:{config.server.port}/users/confirm-email/{token.token}"
        html_content = operations._prepare_mail_template(
            token_type=token.token_type, token=token.token, recipient=user.email
        )

        assert confirmation_link in html_content
        assert user.email in html_content

    @staticmethod
    def test_prepare_mail_template_password_reset_expected_success(use_test_db):
        """
        Test that the email template include the correct url
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)
        confirmation_link = f"{config.server.host}:{config.server.port}/users/reset-password/{token.token}"
        html_content = operations._prepare_mail_template(
            token_type=token.token_type, token=token.token, recipient=user.email
        )

        assert confirmation_link in html_content
        assert user.email in html_content

    @staticmethod
    @pytest.mark.asyncio
    async def test_send_email_expected_success(use_test_db):
        """
        Test send email expected to be successful
        :param use_test_db:
        :return:
        """
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}

            user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
            token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)
            response = await operations.send_email(token=token, recipient=user)

            assert response == {"status": 201}

            mock_send_mail.assert_called_once_with(
                html_content=ANY,
                token_type=token.token_type,
                recipient_email=user.email,
                username=user.username,
            )

    @staticmethod
    @pytest.mark.asyncio
    async def test_send_email_expected_exception(use_test_db):
        """
        Test send email expected to raise exception
        :param use_test_db:
        :return:
        """
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.side_effect = exceptions.FailedToSendEmailException(status_code=400, text="Bad Request")

            user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
            token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)

            with pytest.raises(exceptions.FailedToSendEmailException) as exception_info:
                await operations.send_email(token=token, recipient=user)

            assert exception_info.value.status_code == 400
            assert exception_info.value.text == "Bad Request"

    @staticmethod
    def test_generate_email_password_token_expected_email_confirmation_token(use_test_db):
        """
        Test generate email confirmation token. Expected correct token
        :param use_test_db:
        :return:
        """

        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION)

        assert token.token_type == constants.TokenTypes.EMAIL_CONFIRMATION
        assert token.expired_on > datetime.datetime.utcnow()
        assert token.user_id == user.id

    @staticmethod
    def test_generate_email_password_token_expected_password_reset_token(use_test_db):
        """
        Test generate password reset token. Expected correct token
        :param use_test_db:
        :return:
        """

        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)

        assert token.token_type == constants.TokenTypes.PASSWORD_RESET
        assert token.expired_on > datetime.datetime.utcnow()
        assert token.user_id == user.id

    @staticmethod
    def test_expire_all_existing_tokens_for_user_expected_to_be_expired(use_test_db):
        """
        Test that the existing tokens are expired
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        number_of_tokens = 3
        tokens = []
        for _ in range(number_of_tokens):
            token = operations.generate_email_password_token(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)
            tokens.append(token)
        operations.expire_all_existing_tokens_for_user(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)
        with db.connection.get_session() as session:
            all_tokens = (
                session.query(models.ConfirmationToken)
                .filter(models.ConfirmationToken.token_type == constants.TokenTypes.PASSWORD_RESET)
                .all()
            )
        for idx in range(len(all_tokens) - 1):
            assert all_tokens[idx].created_on == tokens[idx].created_on
            assert tokens[idx].expired_on > datetime.datetime.utcnow()
            assert all_tokens[idx].expired_on < datetime.datetime.utcnow()

    @staticmethod
    def test_check_if_token_is_valid_expected_to_be_valid(use_test_db):
        """
        Check if token is not expired expected to be valid
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        assert operations.check_if_token_is_valid(token=password_token.token) == password_token
        assert operations.check_if_token_is_valid(token=email_token.token) == email_token

    @staticmethod
    def test_check_if_token_is_valid_expected_to_be_expired(use_test_db):
        """
        Check if token is not expired expected to be expired
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        operations.expire_all_existing_tokens_for_user(user=user, token_type=constants.TokenTypes.PASSWORD_RESET)
        operations.expire_all_existing_tokens_for_user(user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION)

        assert operations.check_if_token_is_valid(token=password_token.token) is None
        assert operations.check_if_token_is_valid(token=email_token.token) is None

    @staticmethod
    def test_confirm_email_expected_success(use_test_db):
        """
        Check if email has been confirmed. Expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        user_with_confirmed_email = operations.confirm_email(email_token)

        assert user_with_confirmed_email.is_email_confirmed is True
        assert user_with_confirmed_email.username == user.username
        assert user_with_confirmed_email.email == user.email
        assert email_token.expired_on < datetime.datetime.utcnow()

    @staticmethod
    def test_update_user_password_expected_success(use_test_db):
        """
        Check if password is successfully updated
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        new_password = USER_DATA["password"] + "new"
        user_with_new_password = operations.update_user_password(
            user=user, new_password=new_password, token=password_token
        )
        assert operations.check_password(user=user_with_new_password, password=new_password) is True
        assert operations.check_password(user=user_with_new_password, password=USER_DATA["password"]) is False
        assert password_token.expired_on < datetime.datetime.utcnow()


class TestUserInputModelEmailValidation:
    """
    Tests for UserInputModelEmailValidation
    """

    @staticmethod
    def test_validate_user_valid_email_success_expected(use_test_db):
        """
        Test for email validation with valid email address.
        Expected success
        :return:
        """
        assert input_models.RegisterUserInputModel.validate_user_email(email=USER_DATA["email"]) == USER_DATA["email"]


class TestUserInputModelPasswordValidation:
    """
    Tests for UserInputModelPasswordValidation
    """

    @staticmethod
    def test_validate_user_password_success_expected(use_test_db):
        """
        Test for password validation in prod context.
        Expected success
        :return:
        """

        valid_password = "Password1@"
        validated_password = input_models.RegisterUserInputModel.validate_password(password=valid_password)
        assert validated_password == valid_password

    @staticmethod
    def test_validate_user_short_password_value_error_expected(use_test_db):
        """
        Test for password validation in prod context with short password
        Expected ValueError
        :return:
        """
        invalid_password = "pass"
        try:
            input_models.RegisterUserInputModel.validate_password(password=invalid_password)
        except ValueError as e:
            assert "Password must be at least 8 characters long" in str(e)

    @staticmethod
    def test_validate_user_password_without_uppercase_letter_value_error_expected(
        use_test_db,
    ):
        """
        Test for password validation in prod context with password without uppercase letter
        Expected ValueError
        :return:
        """
        invalid_password = "password"
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert "Password must contain at least one uppercase letter" in str(e)

    @staticmethod
    def test_validate_user_password_without_lowercase_letter_value_error_expected(
        use_test_db,
    ):
        """
        Test for password validation in prod context with password without lowercase letter
        Expected ValueError
        :return:
        """
        invalid_password = "PASSWORD"
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert "Password must contain at least one lowercase letter" in str(e)

    @staticmethod
    def test_validate_user_password_without_digit_value_error_expected(use_test_db):
        """
        Test for password validation in prod context with password without digit
        Expected ValueError
        :return:
        """
        invalid_password = "Password"
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert "Password must contain at least one digit" in str(e)

    @staticmethod
    def test_validate_user_password_special_symbol_value_error_expected(use_test_db):
        """
        Test for password validation in prod context with password without special symbol
        Expected ValueError
        :return:
        """
        invalid_password = "Password1"
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert "Password must contain at least one special symbol: !@#$%^&?" in str(e)


class TestUpdateUserInputModel:
    """
    Tests for UpdateUserInputModel value validation for email field
    """

    @staticmethod
    def test_validate_update_user_valid_filed_success_expected(use_test_db):
        """
        Test for field validation with valid field.
        Expected success
        :return:
        """
        field = "email"
        validated_field = input_models.UpdateUserInputModel.validate_field(field=field)
        assert validated_field == field

    @staticmethod
    def test_validate_update_user_invalid_filed_value_error_expected(use_test_db):
        """
        Test for field validation with invalid field.
        Expected ValueError
        :return:
        """
        invalid_field = "invalid_field"
        try:
            input_models.UpdateUserInputModel.validate_field(field=invalid_field)
        except ValueError as e:
            assert f"You are not allowed to edit {invalid_field} column" in str(e)

    @staticmethod
    def test_validate_value_valid_email_success_expected(use_test_db):
        """
        Test for email validation with valid email address.
        Expected success
        :return:
        """

        valid_email = "test@test.bg"
        validated_email = input_models.UpdateUserInputModel.validate_value(value=valid_email)
        assert validated_email == valid_email


class TestUserEndpoints:
    client = TestClient(app)

    @classmethod
    def test_signup_endpoint_expected_success(cls, use_test_db):
        """
        Test signup user endpoint with valid data. Expected success
        :param use_test_db:
        :return:
        """
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}
            response = cls.client.post("/users/signup/", json=USER_DATA)

            assert response.json()["id"] == 1
            assert response.json()["username"] == USER_DATA["username"]
            assert response.json()["email"] == USER_DATA["email"]
            assert response.json()["roles"] == []
            assert response.status_code == 201
            assert response.json() == {
                "email": "test@mail.com",
                "id": 1,
                "roles": [],
                "username": "test_user",
            }

    @classmethod
    def test_signup_endpoint_user_exists_expected_exception(cls, use_test_db):
        """
        Test signup user endpoint with same user. Expected exception
        :param use_test_db:
        :return:
        """

        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}
            response = cls.client.post("/users/signup/", json=USER_DATA)

        assert response.status_code == 409
        assert response.json()["detail"] == "User with this username or email already exists!"

    @classmethod
    def test_signup_endpoint_failed_to_send_email_expected_exception(cls, use_test_db):
        """
        Test signup user endpoint when sed email fails. Expected exception
        :param use_test_db:
        :return:
        """

        with patch(
            "features.users.operations._send_mail",
            side_effect=exceptions.FailedToSendEmailException(status_code=400, text="Bad Request"),
        ):
            response = cls.client.post("/users/signup/", json=USER_DATA)

        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to send email: Bad Request"

    @classmethod
    def test_signin_endpoint_expected_success(cls, use_test_db):
        """
        Test signin user endpoint. Expected success
        :param use_test_db:
        :return:
        """

        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        payload = {
            "username": USER_DATA["username"],
            "password": USER_DATA["password"],
        }
        response = cls.client.post("/users/signin/", data=payload)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "Bearer"

    @classmethod
    def test_signin_endpoint_wrong_username_expected_exception(cls, use_test_db):
        """
        Test signin user endpoint with wrong username. Expected exception
        :param use_test_db:
        :return:
        """

        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        payload = {"username": "wrong username", "password": USER_DATA["password"]}
        response = cls.client.post("/users/signin/", data=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User does not exist"}

    @classmethod
    def test_signin_endpoint_wrong_password_expected_exception(cls, use_test_db):
        """
        Test signin user endpoint with wrong password. Expected exception
        :param use_test_db:
        :return:
        """

        operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        payload = {"username": USER_DATA["username"], "password": "wrong password"}
        response = cls.client.post("/users/signin/", data=payload)

        assert response.status_code == 403
        assert response.json() == {"detail": "Incorrect username or password"}

    @classmethod
    def test_show_all_users_endpoint_one_user_expected_success(cls, use_test_db):
        """
        Test all users endpoint wit one user. Expected list with one user
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name="Admin", created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        user.roles.append(role)
        token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get("/users/all/", headers=headers)

        assert response.status_code == 200
        assert response.json() == [
            {'email': 'test@mail.com', 'id': 1, 'roles': [{'id': 1, 'name': 'Admin'}], 'username': 'test_user'}
        ]
        assert len(response.json()) == 1

    @classmethod
    def test_show_all_users_endpoint_users_expected_list_with_users(cls, use_test_db):
        """
        Test show all users endpoint. Expected list with all users
        :param use_test_db:
        :return:
        """
        users = 3
        all_users = []
        for i in range(users):
            user = operations.create_new_user(
                user=input_models.RegisterUserInputModel(
                    username=f'{i}{USER_DATA["username"]}',
                    email=f'{i}{USER_DATA["email"]}',
                    password=f'{i}{USER_DATA["password"]}',
                )
            )
            all_users.append(user)

        role = operations.create_role(name="Admin", created_by=all_users[0].id)
        operations.add_user_to_role(user_id=all_users[0].id, role_id=role.id, added_by=all_users[0].id)
        all_users[0].roles.append(role)
        token, _ = operations.create_token(user_id=all_users[0].id, user_role_ids=[x.id for x in all_users[0].roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get("/users/all/", headers=headers)

        assert response.status_code == 200
        assert len(response.json()) == users

    @classmethod
    def test_show_user_endpoint_users_expected_success(cls, use_test_db):
        """
        Test show user endpoint. Expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token, _ = operations.create_token(user_id=user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get(f"/users/{user.id}/", headers=headers)

        assert response.status_code == 200
        assert response.json() == {
            "email": "test@mail.com",
            "id": 1,
            "roles": [],
            "username": "test_user",
        }

    @classmethod
    def test_show_user_endpoint_without_auth_expected_exception(cls, use_test_db):
        """
        Test show user endpoint without auth. Expected exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token, _ = operations.create_token(user_id=user.id)

        response = cls.client.get(f"/users/{user.id}/")

        assert response.status_code == 401

    @classmethod
    def test_show_user_endpoint_with_not_existing_user_id_expected_exception(cls, use_test_db):
        """
        Test show user endpoint without user. Expected exception
        :param use_test_db:
        :return:
        """
        not_existing_user_id = 999
        response = cls.client.get(f"/users/{not_existing_user_id}/")

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}

    @classmethod
    def test_show_user_endpoint_user_is_admin_expected_success(cls, use_test_db):
        """
        Test show user endpoint when user is admin. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get(f"/users/{user.id}/", headers=headers)

        assert response.status_code == 200
        assert response.json() == {
            "email": user.email,
            "id": user.id,
            "roles": user.roles,
            "username": user.username,
        }

    @classmethod
    def test_patch_user_endpoint_user_expected_success(cls, use_test_db):
        """
        Test show user endpoint when user. Expected success
        :param use_test_db:
        :return:
        """

        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token, _ = operations.create_token(user_id=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        new_email = "new@test.com"
        data = {"field": "email", "value": new_email}

        response = cls.client.patch(f"/users/{user.id}/", headers=headers, json=data)

        assert response.status_code == 200
        assert response.json() == {'email': new_email, 'id': user.id, 'roles': user.roles, 'username': user.username}

    @classmethod
    def test_patch_user_endpoint_user_is_admin_expected_success(cls, use_test_db):
        """
        Test show user endpoint when user is admin. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}
        new_email = "new@test.com"
        data = {"field": "email", "value": new_email}

        response = cls.client.patch(f"/users/{user.id}/", headers=headers, json=data)

        assert response.status_code == 200
        assert response.json() == {'email': new_email, 'id': user.id, 'roles': user.roles, 'username': user.username}

    @classmethod
    def test_patch_user_endpoint_with_admin_user_does_not_exist_expected_exception(cls, use_test_db):
        """
        Test show user endpoint when admin and user does not exist. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}
        new_email = "new@test.com"
        data = {"field": "email", "value": new_email}
        not_existing_user_id = 999

        response = cls.client.patch(f"/users/{not_existing_user_id}/", headers=headers, json=data)

        assert response.status_code == 404
        assert response.json() == {'detail': f'User with user_id={not_existing_user_id} does not exist'}

    @classmethod
    def test_get_all_roles_expected_success(cls, use_test_db):
        """
        Test get all roles. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        all_roles = []
        response_roles = []
        total_roles = 3
        role_name = "Admin"
        for i in range(total_roles):
            role = operations.create_role(name=f"{i}{role_name}", created_by=admin.id)
            all_roles.append(role)
            response_roles.append({'id': role.id, 'name': role.name})

        operations.add_user_to_role(user_id=admin.id, role_id=all_roles[0].id, added_by=admin.id)
        admin.roles.append(all_roles[0])
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get("/roles/", headers=headers)

        assert response.status_code == 200
        assert response.json() == response_roles

    @classmethod
    def test_get_all_roles_include_users_expected_success(cls, use_test_db):
        """
        Test get all roles include users. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        all_roles = []
        response_roles = []
        total_roles = 3
        role_name = "Admin"
        for i in range(total_roles):
            role = operations.create_role(name=f"{i}{role_name}", created_by=admin.id)
            all_roles.append(role)
            response_roles.append({'id': role.id, 'name': role.name, "users": []})

        operations.add_user_to_role(user_id=admin.id, role_id=all_roles[0].id, added_by=admin.id)
        admin.roles.append(all_roles[0])
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}
        response_roles[0]["users"].append({'email': admin.email, 'id': admin.id, 'username': admin.username})

        response = cls.client.get("/roles/", headers=headers, params={"include_users": True})

        assert response.status_code == 200
        assert response.json() == response_roles

    @classmethod
    def test_get_role_with_users_expected_success(cls, use_test_db):
        """
        Test get role with users. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)

        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get(f"/roles/{role.id}", headers=headers)

        assert response.status_code == 200
        assert response.json() == {
            'id': role.id,
            'name': role.name,
            'users': [{'email': admin.email, 'id': admin.id, 'username': admin.username}],
        }

    @classmethod
    def test_create_role_endpoint_expected_success(cls, use_test_db):
        """
        Test create role. Expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name="Admin", created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        user.roles.append(role)
        token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])

        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": "new_role"}

        response = cls.client.post("/roles/", headers=headers, json=data)

        assert response.status_code == 201
        assert response.json() == {'id': 2, 'name': 'new_role'}

    @classmethod
    def test_create_role_endpoint_role_exists_expected_exception(cls, use_test_db):
        """
        Test create role when role exists. Expected exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        role = operations.create_role(name="Admin", created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        user.roles.append(role)
        token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])

        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": "Admin"}

        response = cls.client.post("/roles/", headers=headers, json=data)

        assert response.status_code == 409
        assert response.json() == {'detail': 'Role already exist'}

    @classmethod
    def test_add_user_to_role_endpoint_expected_success(cls, use_test_db):
        """
        Test add user to role. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        second_role = operations.create_role(name="Moderator", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(f"/users/{admin.id}/roles/{second_role.id}", headers=headers)

        assert response.status_code == 201

    @classmethod
    def test_add_user_to_role_endpoint_user_does_not_exist_expected_exception(cls, use_test_db):
        """
        Test add user to role with not existing user. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        second_role = operations.create_role(name="Moderator", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(f"/users/{999}/roles/{second_role.id}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'User does not exist'}

    @classmethod
    def test_add_user_to_role_endpoint_role_does_not_exist_expected_exception(cls, use_test_db):
        """
        Test add user to role with not existing role. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(f"/users/{admin.id}/roles/{999}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'Role does not exist'}

    @classmethod
    def test_add_user_to_role_endpoint_user_is_added_to_role_expected_exception(cls, use_test_db):
        """
        Test add user to role when is already added. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(f"/users/{admin.id}/roles/{role.id}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'User already have this role'}

    @classmethod
    def test_remove_user_from_role_endpoint_expected_success(cls, use_test_db):
        """
        Test remove user to role. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.delete(f"/users/{admin.id}/roles/{role.id}", headers=headers)

        assert response.status_code == 204

    @classmethod
    def test_remove_user_from_role_endpoint_user_does_not_exist_expected_exception(cls, use_test_db):
        """
        Test remove user from role with not existing user. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        second_role = operations.create_role(name="Moderator", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.delete(f"/users/{999}/roles/{second_role.id}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'User does not exist'}

    @classmethod
    def test_remove_user_from_role_endpoint_role_does_not_exist_expected_exception(cls, use_test_db):
        """
        Test remove user from role with not existing role. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.delete(f"/users/{admin.id}/roles/{999}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'Role does not exist'}

    @classmethod
    def test_remove_user_from_role_endpoint_user_is_not_added_to_role_expected_exception(cls, use_test_db):
        """
        Test remove user from role when is not added. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.delete(f"/users/{user.id}/roles/{role.id}", headers=headers)

        assert response.status_code == 404
        assert response.json() == {'detail': 'No user with this role'}

    @classmethod
    def test_confirm_email_endpoint_expected_success(cls, use_test_db):
        """
        Test confirm email. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        confirmation_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get(f"/users/confirm-email/{confirmation_token.token}", headers=headers)

        assert response.status_code == 200

    @classmethod
    def test_confirm_email_endpoint_invalid_token_expected_exception(cls, use_test_db):
        """
        Test confirm email with invalid token. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        confirmation_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        operations.expire_all_existing_tokens_for_user(user=admin, token_type=constants.TokenTypes.EMAIL_CONFIRMATION)
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.get(f"/users/confirm-email/{confirmation_token.token}", headers=headers)

        assert response.status_code == 400
        assert response.json() == {'detail': 'Invalid token'}

    @classmethod
    @pytest.mark.asyncio
    async def test_request_password_reset_expected_success(cls, use_test_db):
        """
        Test request password reset expected success
        :param use_test_db:
        :return:
        """
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}

            user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
            token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])
            data = {"email": user.email}
            headers = {"Authorization": f"Bearer {token}"}
            response = cls.client.post("/users/request-password-reset/", headers=headers, params=data)

        assert response.status_code == 200

    @classmethod
    @pytest.mark.asyncio
    async def test_request_password_reset_failed_to_send_email_expected_success(cls, use_test_db):
        """
        Test request password reset failed to send email. Expected exception
        :param use_test_db:
        :return:
        """
        with patch("features.users.operations._send_mail", new_callable=AsyncMock) as mock_send_mail:
            mock_send_mail.side_effect = exceptions.FailedToSendEmailException(status_code=400, text="Bad Request")

            user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
            token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])
            data = {"email": user.email}
            headers = {"Authorization": f"Bearer {token}"}
            response = cls.client.post("/users/request-password-reset/", headers=headers, params=data)

        assert response.status_code == 400
        assert response.json() == {'detail': 'Failed to send email: Bad Request'}

    @classmethod
    @pytest.mark.asyncio
    async def test_request_password_reset_invalid_email_expected_success(cls, use_test_db):
        """
        Test request password reset with invalid email. Expected exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(user=input_models.RegisterUserInputModel(**USER_DATA))
        token, _ = operations.create_token(user_id=user.id, user_role_ids=[x.id for x in user.roles])
        data = {"email": "invalid_email@test.com"}
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post("/users/request-password-reset/", headers=headers, params=data)

        assert response.status_code == 404
        assert response.json() == {'detail': 'User not found'}

    @classmethod
    def test_reset_password_endpoint_expected_success(cls, use_test_db):
        """
        Test reset password. Expected success
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        new_password = "NewPassword1@"

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        reset_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(
            f"/users/reset-password/{reset_token.token}/?new_password={new_password}",
            headers=headers,
        )

        assert response.status_code == 200

    @classmethod
    def test_reset_password_endpoint_with_invalid_token_expected_exception(cls, use_test_db):
        """
        Test reset password with invalid token. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        new_password = "NewPassword1@"

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        reset_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        operations.expire_all_existing_tokens_for_user(user=admin, token_type=constants.TokenTypes.PASSWORD_RESET)
        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(
            f"/users/reset-password/{reset_token.token}/?new_password={new_password}",
            headers=headers,
        )

        assert response.status_code == 400
        assert response.json() == {'detail': 'Invalid token'}

    @classmethod
    def test_reset_password_endpoint_with_same_password_expected_exception(cls, use_test_db):
        """
        Test reset password with same password. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        new_password = "adminPassword1@"

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        reset_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.PASSWORD_RESET
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(
            f"/users/reset-password/{reset_token.token}/?new_password={new_password}",
            headers=headers,
        )

        assert response.status_code == 422
        assert response.json() == {'detail': 'The new password can not be the same as the old password'}

    @classmethod
    def test_reset_password_endpoint_with_invalid_password_expected_exception(cls, use_test_db):
        """
        Test reset password with invalid password. Expected exception
        :param use_test_db:
        :return:
        """
        admin = operations.create_new_user(
            user=input_models.RegisterUserInputModel(
                username="admin", email="admin@admin.com", password="adminPassword1@"
            )
        )
        new_password = "p@"

        role = operations.create_role(name="Admin", created_by=admin.id)
        operations.add_user_to_role(user_id=admin.id, role_id=role.id, added_by=admin.id)
        admin.roles.append(role)
        token, _ = operations.create_token(user_id=admin.id, user_role_ids=[x.id for x in admin.roles])
        reset_token = operations.generate_email_password_token(
            user=admin, token_type=constants.TokenTypes.PASSWORD_RESET
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = cls.client.post(
            f"/users/reset-password/{reset_token.token}/?new_password={new_password}",
            headers=headers,
        )

        assert response.status_code == 422
        assert "detail" in response.json()
