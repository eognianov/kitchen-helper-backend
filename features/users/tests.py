import bcrypt
import pytest
import db.connection
from tests.fixtures import use_test_db
from features.users import operations, models, input_models, exceptions
from fastapi.testclient import TestClient
from api import app


class TestUserOperations:
    """
    Tests for user operations
    """
    client = TestClient(app)
    user_data = {
        'username': 'test_user',
        'email': '_test_example@abv.bg',
        'password': 'Password1@'
    }

    def test_hashed_password_matches_expected(self, use_test_db, mocker):
        """
        Test that hashed password
        :param use_test_db:
        :param mocker:
        :return:
        """
        password = "secure_password"
        hashed_password = operations._hash_password(password)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed_password) is True

    def test_check_password_expected_true(self, use_test_db, mocker):
        """
        Test that password is equal to user's hashed password
        :param use_test_db:
        :param mocker:
        :return:
        """
        assert operations.check_password(
            operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data)),
            self.user_data['password']
        ) is True

    def test_check_password_expected_false(self, use_test_db, mocker):
        """
        Test that password is different from user's hashed password
        :param use_test_db:
        :param mocker:
        :return:
        """
        different_password = 'different password'
        assert operations.check_password(
            operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data)),
            different_password
        ) is False

    def test_create_new_user_without_role_success(self, use_test_db, mocker):
        """
        Test that creating user without role is successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            users = session.query(models.User).all()
        assert users[0].username == self.user_data['username']
        assert users[0].email == self.user_data['email']
        assert users[0].id == 1
        assert users[0].roles == []

    def test_create_new_user_with_roles_success(self, use_test_db, mocker):
        """
        Test that creating user with role is successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        operations.create_role('admin', 'me')

        with db.connection.get_session() as session:
            user = session.query(models.User).first()
            role = session.query(models.Role).first()
            operations.add_user_to_role(user.id, role.id, 'me')
            session.commit()
            updated_user = session.query(models.User).get(user.id)

        assert updated_user.username == self.user_data['username']
        assert updated_user.email == self.user_data['email']
        assert updated_user.id == 1
        assert len(updated_user.roles) == 1

    def test_signin_user_expected_success(self, use_test_db, mocker):
        """
        Test that signin user is successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            user = session.query(models.User).first()
        assert operations.signin_user(self.user_data['username'], self.user_data['password']) == user

    def test_signin_user_not_existing_username_expected_exception(self, use_test_db, mocker):
        """
        Test that signin user with not existing username is not successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        different_username = 'different_username'
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.signin_user(different_username, self.user_data['password'])

    def test_signin_user_wrong_password_expected_exception(self, use_test_db, mocker):
        """
        Test that signin user with wrong password is not successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        wrong_password = 'wrong_password'
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with pytest.raises(exceptions.AccessDenied):
            operations.signin_user(self.user_data['username'], wrong_password)


class TestUserInputModelEmailValidation:
    """
    Tests for UserInputModelEmailValidation
    """
    client = TestClient(app)
    user_data = {
        'username': 'test_user',
        'password': 'secure_password!2'
    }

    def test_validate_user_valid_email_success_expected(self, use_test_db, mocker):
        """
        Test for email validation with valid email address.
        Expected success
        :return:
        """
        self.user_data['email'] = '_test_example@test.bg'
        valid_email = self.user_data['email']
        validated_email = input_models.RegisterUserInputModel.validate_user_email(valid_email)
        assert validated_email == valid_email


class TestUserInputModelPasswordValidation:
    """
    Tests for UserInputModelPasswordValidation
    """
    client = TestClient(app)

    def test_validate_user_password_success_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context.
        Expected success
        :return:
        """

        valid_password = 'Password1@'
        validated_password = input_models.RegisterUserInputModel.validate_password(valid_password)
        assert validated_password == valid_password

    def test_validate_user_short_password_value_error_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context with short password
        Expected ValueError
        :return:
        """
        invalid_password = 'pass'
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert 'Password must be at least 8 characters long' in str(e)

    def test_validate_user_password_without_uppercase_letter_value_error_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context with password without uppercase letter
        Expected ValueError
        :return:
        """
        invalid_password = 'password'
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert 'Password must contain at least one uppercase letter' in str(e)

    def test_validate_user_password_without_lowercase_letter_value_error_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context with password without lowercase letter
        Expected ValueError
        :return:
        """
        invalid_password = 'PASSWORD'
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert 'Password must contain at least one lowercase letter' in str(e)

    def test_validate_user_password_without_digit_value_error_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context with password without digit
        Expected ValueError
        :return:
        """
        invalid_password = 'Password'
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert 'Password must contain at least one digit' in str(e)

    def test_validate_user_password_special_symbol_value_error_expected(self, use_test_db, mocker):
        """
        Test for password validation in prod context with password without special symbol
        Expected ValueError
        :return:
        """
        invalid_password = 'Password1'
        try:
            input_models.RegisterUserInputModel.validate_password(invalid_password)
        except ValueError as e:
            assert 'Password must contain at least one special symbol: !@#$%^&?' in str(e)


class TestUpdateUserInputModel:
    """
    Tests for UpdateUserInputModel value validation for email field
    """
    client = TestClient(app)

    def test_validate_update_user_valid_filed_success_expected(self, use_test_db, mocker):
        """
        Test for field validation with valid field.
        Expected success
        :return:
        """
        validated_email = input_models.UpdateUserInputModel.validate_field('email')
        assert validated_email == 'email'

    def test_validate_update_user_invalid_filed_value_error_expected(self, use_test_db, mocker):
        """
        Test for field validation with invalid field.
        Expected ValueError
        :return:
        """
        invalid_field = 'invalid_field'
        try:
            input_models.UpdateUserInputModel.validate_field(invalid_field)
        except ValueError as e:
            assert f"You are not allowed to edit {invalid_field} column" in str(e)

    def test_validate_value_valid_email_success_expected(self, use_test_db, mocker):
        """
        Test for email validation with valid email address.
        Expected success
        :return:
        """

        valid_email = 'test@test.bg'
        validated_email = input_models.UpdateUserInputModel.validate_value(valid_email)
        assert validated_email == valid_email
