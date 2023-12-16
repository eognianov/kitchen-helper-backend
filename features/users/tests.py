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


class TestUserOperations:
    """
    Tests for user operations
    """

    client = TestClient(app)
    USER_DATA = {
        "username": "test_user",
        "email": "test@test.com",
        "password": "Password1@",
    }

    ROLE_DATA = {"name": "admin"}

    config = configuration.Config()

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

    @classmethod
    def test_check_password_expected_true(cls, use_test_db):
        """
        Test that password is equal to user's hashed password
        :param use_test_db:
        :return:
        """
        assert (
            operations.check_password(
                operations.create_new_user(
                    user=input_models.RegisterUserInputModel(**cls.USER_DATA)
                ),
                cls.USER_DATA["password"],
            )
            is True
        )

    @classmethod
    def test_check_password_expected_false(cls, use_test_db):
        """
        Test that password is different from user's hashed password
        :param use_test_db:
        :return:
        """
        different_password = "different password"
        assert (
            operations.check_password(
                user=operations.create_new_user(
                    user=input_models.RegisterUserInputModel(**cls.USER_DATA)
                ),
                password=different_password,
            )
            is False
        )

    @classmethod
    def test_create_new_user_without_role_success(cls, use_test_db):
        """
        Test that creating user without role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        assert user.username == cls.USER_DATA["username"]
        assert user.email == cls.USER_DATA["email"]
        assert user.id == 1
        assert user.roles == []

    @classmethod
    def test_create_new_user_with_roles_success(cls, use_test_db):
        """
        Test that creating user with role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        updated_user = operations.get_user_from_db(pk=user.id)

        assert updated_user.username == cls.USER_DATA["username"]
        assert updated_user.email == cls.USER_DATA["email"]
        assert updated_user.id == 1
        assert len(updated_user.roles) == 1
        assert updated_user.roles[0] == role

    @classmethod
    def test_signin_user_expected_success(cls, use_test_db):
        """
        Test that signin user is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        assert (
            operations.signin_user(
                username=cls.USER_DATA["username"], password=cls.USER_DATA["password"]
            )
            == user
        )

    @classmethod
    def test_signin_user_not_existing_username_expected_exception(cls, use_test_db):
        """
        Test that signin user with not existing username is not successful
        :param use_test_db:
        :return:
        """
        different_username = "different_username"
        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.signin_user(
                username=different_username, password=cls.USER_DATA["password"]
            )

    @classmethod
    def test_signin_user_wrong_password_expected_exception(cls, use_test_db):
        """
        Test that signin user with wrong password is not successful
        :param use_test_db:
        :return:
        """
        wrong_password = "wrong_password"
        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        with pytest.raises(exceptions.AccessDenied):
            operations.signin_user(cls.USER_DATA["username"], wrong_password)

    @classmethod
    def test_get_user_from_db_with_pk_expected_success(cls, use_test_db):
        """
        Test get user from database with pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        assert operations.get_user_from_db(pk=user.id) == user

    @classmethod
    def test_get_user_from_db_with_wrong_pk_expected_exception(cls, use_test_db):
        """
        Test get user from database with wrong pk
        :param use_test_db:
        :return:
        """
        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(pk=2)

    @classmethod
    def test_get_user_from_db_with_username_expected_success(cls, use_test_db):
        """
        Test get user from database with username
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        assert operations.get_user_from_db(username=user.username) == user

    @classmethod
    def test_get_user_from_db_with_wrong_username_expected_exception(cls, use_test_db):
        """
        Test get user from database with wrong username
        :param use_test_db:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**cls.USER_DATA))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(username="wrong_username")

    @classmethod
    def test_get_user_from_db_with_email_expected_success(cls, use_test_db):
        """
        Test get user from database with email
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        assert operations.get_user_from_db(email=user.email) == user

    @classmethod
    def test_get_user_from_db_with_wrong_email_expected_exception(cls, use_test_db):
        """
        Test get user from database with wrong email
        :param use_test_db:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**cls.USER_DATA))
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

    @classmethod
    def test_get_all_users_one_user_in_database_expected_list_with_one_user(
        cls, use_test_db
    ):
        """
        Test get all users from database with one user in the database
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        all_users = operations.get_all_users()
        assert all_users[0] == user
        assert len(all_users) == 1

    @classmethod
    def test_get_all_users_more_users_in_database_expected_list_with_same_users(
        cls, use_test_db
    ):
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
                        username=f"{cls.USER_DATA['username']}{i}",
                        email=f"{i}{cls.USER_DATA['email']}",
                        password=cls.USER_DATA["password"],
                    )
                )
            )
        all_users = operations.get_all_users()
        assert all_users[0] == users[0]
        assert all_users[len(all_users) - 1] == users[len(users) - 1]
        assert len(all_users) == total_users

    @classmethod
    def test_update_user_expected_user_to_be_updated(cls, use_test_db):
        """
        Test update user with expected user data
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        new_email = "updated@tets.com"
        updated_user = operations.update_user(
            user_id=user.id, field="email", value=new_email, updated_by=user.id
        )
        assert updated_user.email == new_email

    @classmethod
    def test_create_token_expected_bearer_token_type(cls, use_test_db):
        """
        Test create token with expected token type (access token) to be created
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        _, token_type = operations.create_token(user_id=user.id)
        assert token_type == "Bearer"

    @classmethod
    def test_create_token_expected_refresh_token_type(cls, use_test_db):
        """
        Test create token with expected token type (refresh token) to be created
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
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

    @classmethod
    def test_get_all_roles_one_role_in_database_expected_list_with_one_role(
        cls, use_test_db
    ):
        """
        Test get all roles from database with one role in the database
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        all_roles = operations.get_all_roles()
        assert all_roles[0] == role
        assert len(all_roles) == 1
        assert all_roles[0].name == role.name
        assert all_roles[0].created_by == user.id

    @classmethod
    def test_get_all_roles_more_roles_in_database_expected_list_with_same_len(
        cls, use_test_db
    ):
        """
        Test get all roles from database with three role in the database
        :param use_test_db:
        :return:
        """
        number_of_roles = 3
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        roles = []
        for i in range(number_of_roles):
            roles.append(
                operations.create_role(
                    name=f"{cls.ROLE_DATA['name']}{i}", created_by=user.id
                )
            )

        all_roles = operations.get_all_roles()
        assert all_roles[0] == roles[0]
        assert all_roles[len(all_roles) - 1] == roles[len(roles) - 1]
        assert len(all_roles) == number_of_roles
        assert all_roles[0].name == roles[0].name
        for role in all_roles:
            assert role.created_by == user.id

    @classmethod
    def test_get_role_with_pk_expected_success(cls, use_test_db):
        """
        Test get role from database with pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        assert operations.get_role(pk=role.id) == role

    @classmethod
    def test_get_role_with_wrong_pk_expected_exception(cls, use_test_db):
        """
        Test get role from database with wrong pk
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(pk=2)

    @classmethod
    def test_get_role_with_name_expected_success(cls, use_test_db):
        """
        Test get role from database with role name
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        assert operations.get_role(role_name=role.name) == role

    @classmethod
    def test_get_role_with_wrong_name_expected_exception(cls, use_test_db):
        """
        Test get role from database with wrong name
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(role_name="wrong_name")

    @staticmethod
    def test_get_role_without_params_expected_exception(use_test_db):
        try:
            operations.get_role()
        except ValueError as e:
            assert "Neither pk nor role_name is provided" in str(e)

    @classmethod
    def test_check_user_role_expected_true(cls, use_test_db):
        """
        Test check user role expected role to be in user's roles
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(user_id=user.id, role_id=role.id, added_by=user.id)
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is True

    @classmethod
    def test_check_user_role_expected_false(cls, use_test_db):
        """
        Test check user role expected role not to be in user's roles
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is False

    @classmethod
    def test_create_role_expected_success(cls, use_test_db):
        """
        Test that creating role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        assert role.name == cls.ROLE_DATA["name"]
        assert role.created_by == user.id
        assert role.id == 1

    @classmethod
    def test_create_same_role_expected_exception(cls, use_test_db):
        """
        Test that creating same role will raise exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.RoleAlreadyExists):
            operations.create_role(cls.ROLE_DATA["name"], created_by=user.id)

    @classmethod
    def test_add_user_to_role_expected_success(cls, use_test_db):
        """
        Test adding user to role is successful
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(cls.ROLE_DATA["name"], created_by=user.id)
        user_roles = user.roles
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        db_user = operations.get_user_from_db(pk=user.id)

        assert db_user.roles[0] == role
        assert len(db_user.roles) == len(user_roles) + 1
        assert db_user.roles == [role]

    @classmethod
    def test_add_user_to_role_user_already_added_expected_exception(cls, use_test_db):
        """
        Test adding user to role when already added raise exception
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        with pytest.raises(exceptions.UserWithRoleExist):
            operations.add_user_to_role(
                role_id=role.id, user_id=user.id, added_by=user.id
            )

    @classmethod
    def test_remove_user_from_role_user_not_added_expected_exception(cls, use_test_db):
        """
        Test removing user from role when not added raise exception expected
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(name=cls.ROLE_DATA["name"], created_by=user.id)
        with pytest.raises(exceptions.UserWithRoleDoesNotExist):
            operations.remove_user_from_role(
                role_id=role.id, user_id=user.id, removed_by=user.id
            )

    @classmethod
    def test_remove_user_from_role_when_user_is_added_expected_success(
        cls, use_test_db
    ):
        """
        Test removing user from role when added expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        role = operations.create_role(cls.ROLE_DATA["name"], created_by=user.id)
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by=user.id)
        user_roles = operations.get_user_from_db(pk=user.id).roles
        operations.remove_user_from_role(
            user_id=user.id, role_id=role.id, removed_by=user.id
        )
        db_user = operations.get_user_from_db(pk=user.id)

        assert db_user.roles != user_roles
        assert len(db_user.roles) == len(user_roles) - 1
        assert db_user.roles == []

    @classmethod
    def test__prepare_mail_template_email_confirmation_expected_success(
        cls, use_test_db
    ):
        """
        Test that the email template include the correct url
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        confirmation_link = f"{cls.config.server.host}:{cls.config.server.port}/users/confirm-email/{token.token}"
        html_content = operations._prepare_mail_template(
            token_type=token.token_type, token=token.token, recipient=user.email
        )

        assert confirmation_link in html_content
        assert user.email in html_content

    @classmethod
    def test__prepare_mail_template_password_reset_expected_success(cls, use_test_db):
        """
        Test that the email template include the correct url
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        confirmation_link = f"{cls.config.server.host}:{cls.config.server.port}/users/reset-password/{token.token}"
        html_content = operations._prepare_mail_template(
            token_type=token.token_type, token=token.token, recipient=user.email
        )

        assert confirmation_link in html_content
        assert user.email in html_content

    @classmethod
    @pytest.mark.asyncio
    async def test_send_email_expected_success(cls, use_test_db):
        """
        Test send email expected to be successful
        :param use_test_db:
        :return:
        """
        with patch(
            "features.users.operations._send_mail", new_callable=AsyncMock
        ) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}

            user = operations.create_new_user(
                user=input_models.RegisterUserInputModel(**cls.USER_DATA)
            )
            token = operations.generate_email_password_token(
                user=user, token_type=constants.TokenTypes.PASSWORD_RESET
            )
            response = await operations.send_email(token=token, recipient=user)

            assert response == {"status": 201}

            mock_send_mail.assert_called_once_with(
                html_content=ANY,
                token_type=token.token_type,
                recipient_email=user.email,
                username=user.username,
            )

    @classmethod
    @pytest.mark.asyncio
    async def test_send_email_expected_exception(cls, use_test_db):
        """
        Test send email expected to raise exception
        :param use_test_db:
        :return:
        """
        with patch(
            "features.users.operations._send_mail", new_callable=AsyncMock
        ) as mock_send_mail:
            mock_send_mail.side_effect = exceptions.FailedToSendEmailException(
                status_code=400, text="Bad Request"
            )

            user = operations.create_new_user(
                user=input_models.RegisterUserInputModel(**cls.USER_DATA)
            )
            token = operations.generate_email_password_token(
                user=user, token_type=constants.TokenTypes.PASSWORD_RESET
            )

            with pytest.raises(exceptions.FailedToSendEmailException) as exception_info:
                await operations.send_email(token=token, recipient=user)

            assert exception_info.value.status_code == 400
            assert exception_info.value.text == "Bad Request"

    @classmethod
    def test_generate_email_password_token_expected_email_confirmation_token(
        cls, use_test_db
    ):
        """
        Test generate email confirmation token. Expected correct token
        :param use_test_db:
        :return:
        """

        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )

        assert token.token_type == constants.TokenTypes.EMAIL_CONFIRMATION
        assert token.expired_on > datetime.datetime.utcnow()
        assert token.user_id == user.id

    @classmethod
    def test_generate_email_password_token_expected_password_reset_token(
        cls, use_test_db
    ):
        """
        Test generate password reset token. Expected correct token
        :param use_test_db:
        :return:
        """

        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )

        assert token.token_type == constants.TokenTypes.PASSWORD_RESET
        assert token.expired_on > datetime.datetime.utcnow()
        assert token.user_id == user.id

    @classmethod
    def test_expire_all_existing_tokens_for_user_expected_to_be_expired(
        cls, use_test_db
    ):
        """
        Test that the existing tokens are expired
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        number_of_tokens = 3
        tokens = []
        for _ in range(number_of_tokens):
            token = operations.generate_email_password_token(
                user=user, token_type=constants.TokenTypes.PASSWORD_RESET
            )
            tokens.append(token)
        operations.expire_all_existing_tokens_for_user(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        with db.connection.get_session() as session:
            all_tokens = (
                session.query(models.ConfirmationToken)
                .filter(
                    models.ConfirmationToken.token_type
                    == constants.TokenTypes.PASSWORD_RESET
                )
                .all()
            )
        for idx in range(len(all_tokens) - 1):
            assert all_tokens[idx].created_on == tokens[idx].created_on
            assert tokens[idx].expired_on > datetime.datetime.utcnow()
            assert all_tokens[idx].expired_on < datetime.datetime.utcnow()

    @classmethod
    def test_check_if_token_is_valid_expected_to_be_valid(cls, use_test_db):
        """
        Check if token is not expired expected to be valid
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        assert (
            operations.check_if_token_is_valid(token=password_token.token)
            == password_token
        )
        assert (
            operations.check_if_token_is_valid(token=email_token.token) == email_token
        )

    @classmethod
    def test_check_if_token_is_valid_expected_to_be_expired(cls, use_test_db):
        """
        Check if token is not expired expected to be expired
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        operations.expire_all_existing_tokens_for_user(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        operations.expire_all_existing_tokens_for_user(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )

        assert operations.check_if_token_is_valid(token=password_token.token) is None
        assert operations.check_if_token_is_valid(token=email_token.token) is None

    @classmethod
    def test_confirm_email_expected_success(cls, use_test_db):
        """
        Check if email has been confirmed. Expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        email_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.EMAIL_CONFIRMATION
        )
        user_with_confirmed_email = operations.confirm_email(email_token)

        assert user_with_confirmed_email.is_email_confirmed is True
        assert user_with_confirmed_email.username == user.username
        assert user_with_confirmed_email.email == user.email
        assert email_token.expired_on < datetime.datetime.utcnow()

    @classmethod
    def test_update_user_password_expected_success(cls, use_test_db):
        """
        Check if password is successfully updated
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        password_token = operations.generate_email_password_token(
            user=user, token_type=constants.TokenTypes.PASSWORD_RESET
        )
        new_password = cls.USER_DATA["password"] + "new"
        user_with_new_password = operations.update_user_password(
            user=user, new_password=new_password, token=password_token
        )
        assert (
            operations.check_password(
                user=user_with_new_password, password=new_password
            )
            is True
        )
        assert (
            operations.check_password(
                user=user_with_new_password, password=cls.USER_DATA["password"]
            )
            is False
        )
        assert password_token.expired_on < datetime.datetime.utcnow()


class TestUserInputModelEmailValidation:
    """
    Tests for UserInputModelEmailValidation
    """

    USER_DATA = {
        "username": "test_user",
        "email": "test@test.com",
        "password": "Password1@",
    }

    @classmethod
    def test_validate_user_valid_email_success_expected(cls, use_test_db):
        """
        Test for email validation with valid email address.
        Expected success
        :return:
        """
        assert (
            input_models.RegisterUserInputModel.validate_user_email(
                email=cls.USER_DATA["email"]
            )
            == cls.USER_DATA["email"]
        )


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
        validated_password = input_models.RegisterUserInputModel.validate_password(
            password=valid_password
        )
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
            input_models.RegisterUserInputModel.validate_password(
                password=invalid_password
            )
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
            assert "Password must contain at least one special symbol: !@#$%^&?" in str(
                e
            )


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
        validated_email = input_models.UpdateUserInputModel.validate_value(
            value=valid_email
        )
        assert validated_email == valid_email


class TestUserEndpoints:
    client = TestClient(app)

    USER_DATA = {
        "username": "test_user",
        "email": "test@mail.com",
        "password": "Password!@",
    }

    @classmethod
    def test_signup_endpoint_expected_success(cls, use_test_db):
        """
        Test signup user endpoint with valid data. Expected success
        :param use_test_db:
        :return:
        """
        with patch(
            "features.users.operations._send_mail", new_callable=AsyncMock
        ) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}
            response = cls.client.post("/users/signup/", json=cls.USER_DATA)

            with db.connection.get_session() as session:
                user = session.query(models.User).first()

            assert user.id == 1
            assert user.username == cls.USER_DATA["username"]
            assert user.email == cls.USER_DATA["email"]
            assert user.roles == []
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

        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        with patch(
            "features.users.operations._send_mail", new_callable=AsyncMock
        ) as mock_send_mail:
            mock_send_mail.return_value = {"status": 201}
            response = cls.client.post("/users/signup/", json=cls.USER_DATA)

        assert response.status_code == 409
        assert (
            response.json()["detail"]
            == "User with this username or email already exists!"
        )

    @classmethod
    def test_signup_endpoint_failed_to_send_email_expected_exception(cls, use_test_db):
        """
        Test signup user endpoint when sed email fails. Expected exception
        :param use_test_db:
        :return:
        """

        with patch(
            "features.users.operations._send_mail",
            side_effect=exceptions.FailedToSendEmailException(
                status_code=400, text="Bad Request"
            ),
        ):
            response = cls.client.post("/users/signup/", json=cls.USER_DATA)

        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to send email: Bad Request"

    @classmethod
    def test_signin_endpoint_expected_success(cls, use_test_db):
        """
        Test signin user endpoint. Expected success
        :param use_test_db:
        :return:
        """

        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        payload = {
            "username": cls.USER_DATA["username"],
            "password": cls.USER_DATA["password"],
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

        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        payload = {"username": "wrong username", "password": cls.USER_DATA["password"]}
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

        operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        payload = {"username": cls.USER_DATA["username"], "password": "wrong password"}
        response = cls.client.post("/users/signin/", data=payload)

        assert response.status_code == 403
        assert response.json() == {"detail": "Incorrect username or password"}

    @classmethod
    def test_show_all_users_endpoint_no_users_expected_empty_list(cls, use_test_db):
        """
        Test all users endpoint without users. Expected empty list
        :param use_test_db:
        :return:
        """

        response = cls.client.get("/users/all/")

        assert response.status_code == 200
        assert response.json() == []
        assert len(response.json()) == 0

    @classmethod
    def test_show_all_users_endpoint_users_expected_list_with_users(cls, use_test_db):
        """
        Test all users endpoint. Expected list with all users
        :param use_test_db:
        :return:
        """
        users = 3
        all_users = []
        for i in range(users):
            user = operations.create_new_user(
                user=input_models.RegisterUserInputModel(
                    username=f'{i}{cls.USER_DATA["username"]}',
                    email=f'{i}{cls.USER_DATA["email"]}',
                    password=f'{i}{cls.USER_DATA["password"]}',
                )
            )
            all_users.append(
                {
                    "email": user.email,
                    "id": user.id,
                    "roles": user.roles,
                    "username": user.username,
                }
            )

        response = cls.client.get("/users/all/")

        assert response.status_code == 200
        assert response.json() == all_users
        assert len(response.json()) == users

    @classmethod
    def test_show_user_endpoint_users_expected_success(cls, use_test_db):
        """
        Test show user endpoint. Expected success
        :param use_test_db:
        :return:
        """
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
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
        user = operations.create_new_user(
            user=input_models.RegisterUserInputModel(**cls.USER_DATA)
        )
        token, _ = operations.create_token(user_id=user.id)

        response = cls.client.get(f"/users/{user.id}/")

        assert response.status_code == 401

    @classmethod
    def test_show_user_endpoint_with_not_existing_user_id_expected_exception(
        cls, use_test_db
    ):
        """
        Test show user endpoint without user. Expected exception
        :param use_test_db:
        :return:
        """
        not_existing_user_id = 999
        response = cls.client.get(f"/users/{not_existing_user_id}/")

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}
