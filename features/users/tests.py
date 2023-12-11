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
        'email': 'test@test.com',
        'password': 'Password1@'
    }

    role_data = {'name': 'admin'}

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

    def test_get_user_from_db_with_pk_expected_success(self, use_test_db, mocker):
        """
        Test get user from database with pk
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            user = session.query(models.User).first()
        assert operations.get_user_from_db(pk=user.id) == user

    def test_get_user_from_db_with_wrong_pk_expected_exception(self, use_test_db, mocker):
        """
        Test get user from database with wrong pk
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(pk=2)

    def test_get_user_from_db_with_username_expected_success(self, use_test_db, mocker):
        """
        Test get user from database with username
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            user = session.query(models.User).first()
        assert operations.get_user_from_db(username=user.username) == user

    def test_get_user_from_db_with_wrong_username_expected_exception(self, use_test_db, mocker):
        """
        Test get user from database with wrong username
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(username='wrong_username')

    def test_get_user_from_db_with_email_expected_success(self, use_test_db, mocker):
        """
        Test get user from database with email
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            user = session.query(models.User).first()
        assert operations.get_user_from_db(email=user.email) == user

    def test_get_user_from_db_with_wrong_email_expected_exception(self, use_test_db, mocker):
        """
        Test get user from database with wrong email
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        with pytest.raises(exceptions.UserDoesNotExistException):
            operations.get_user_from_db(email='wrong_email@test.com')

    def test_get_all_users_no_users_in_database_expected_empty_list(self, use_test_db, mocker):
        """
        Test get all users from database without users in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        all_users = operations.get_all_users()
        assert all_users == []
        assert len(all_users) == 0

    def test_get_all_users_one_user_in_database_expected_list_with_one_user(self, use_test_db, mocker):
        """
        Test get all users from database with one user in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        all_users = operations.get_all_users()
        with db.connection.get_session() as session:
            user = session.query(models.User).first()
        assert all_users[0] == user
        assert len(all_users) == 1

    def test_get_all_users_five_users_in_database_expected_list_with_five_users(self, use_test_db, mocker):
        """
        Test get all users from database with five users in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        for i in range(5):
            operations.create_new_user(input_models.RegisterUserInputModel(
                username=f"{self.user_data['username']}{i}",
                email=f"{i}{self.user_data['email']}",
                password=self.user_data['password']
            ))
        all_users = operations.get_all_users()
        with db.connection.get_session() as session:
            users = session.query(models.User).all()
        assert all_users[0] == users[0]
        assert all_users[len(all_users) - 1] == users[len(users) - 1]
        assert len(all_users) == 5

    def test_update_user_expected_user_to_be_updated(self, use_test_db, mocker):
        """
        Test update user with expected user data
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        new_email = 'updated@tets.com'
        operations.update_user(user.id, 'email', new_email, user.id)
        with db.connection.get_session() as session:
            updated_user = session.query(models.User).first()
        assert updated_user.email == new_email

    def test_create_token_expected_access_token_type(self, use_test_db, mocker):
        """
        Test create token with expected token type (access token) to be created
        :param use_test_db:
        :param mocker:
        :return:
        """
        token, token_type = operations.create_token(subject=self.user_data['username'])
        assert token_type == 'jwt access token'

    def test_create_token_expected_refresh_token_type(self, use_test_db, mocker):
        """
        Test create token with expected token type (refresh token) to be created
        :param use_test_db:
        :param mocker:
        :return:
        """
        token, token_type = operations.create_token(subject=self.user_data['username'], access=False)
        assert token_type == 'jwt refresh token'

    def test_get_all_roles_no_roles_in_database_expected_empty_list(self, use_test_db, mocker):
        """
        Test get all roles from database without roles in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        all_roles = operations.get_all_roles()
        assert all_roles == []
        assert len(all_roles) == 0

    def test_get_all_roles_one_role_in_database_expected_list_with_one_role(self, use_test_db, mocker):
        """
        Test get all roles from database with one role in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        operations.create_role(self.role_data['name'], 'me')  # TODO: Change created_by to user.id
        all_roles = operations.get_all_roles()
        with db.connection.get_session() as session:
            role_from_db = session.query(models.Role).first()
        assert all_roles[0] == role_from_db
        assert len(all_roles) == 1
        assert all_roles[0].name == self.role_data['name']
        assert all_roles[0].created_by == 'me'  # TODO: Change 'me' with user.id

    def test_get_all_roles_more_roles_in_database_expected_list_with_same_len(self, use_test_db, mocker):
        """
        Test get all roles from database with three role in the database
        :param use_test_db:
        :param mocker:
        :return:
        """
        number_of_roles = 3
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        for i in range(number_of_roles):
            operations.create_role(f"{self.role_data['name']}{i}", 'me')  # TODO: Change created_by to user.id
        all_roles = operations.get_all_roles()
        with db.connection.get_session() as session:
            roles_from_db = session.query(models.Role).all()
        assert all_roles[0] == roles_from_db[0]
        assert all_roles[len(all_roles) - 1] == roles_from_db[len(roles_from_db) - 1]
        assert len(all_roles) == number_of_roles
        assert all_roles[0].name == roles_from_db[0].name
        for role in all_roles:
            assert role.created_by == 'me'  # TODO: Change 'me' with user.id

    def test_get_role_with_pk_expected_success(self, use_test_db, mocker):
        """
        Test get role from database with pk
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        with db.connection.get_session() as session:
            db_role = session.query(models.Role).first()
        assert operations.get_role(pk=role.id) == db_role

    def test_get_role_with_wrong_pk_expected_exception(self, use_test_db, mocker):
        """
        Test get role from database with wrong pk
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(pk=2)

    def test_get_role_with_name_expected_success(self, use_test_db, mocker):
        """
        Test get role from database with role name
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        with db.connection.get_session() as session:
            db_role = session.query(models.Role).first()
        assert operations.get_role(role_name=role.name) == db_role

    def test_get_role_with_wrong_name_expected_exception(self, use_test_db, mocker):
        """
        Test get role from database with wrong name
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        with pytest.raises(exceptions.RoleDoesNotExistException):
            operations.get_role(role_name='wrong_name')

    def test_check_user_role_expected_true(self, use_test_db, mocker):
        """
        Test check user role expected role to be in user's roles
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        operations.add_user_to_role(user_id=user.id, role_id=role.id)
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is True

    def test_check_user_role_expected_false(self, use_test_db, mocker):
        """
        Test check user role expected role not to be in user's roles
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        assert operations.check_user_role(user_id=user.id, role_id=role.id) is False

    def test_create_role_expected_success(self, use_test_db, mocker):
        """
        Test that creating role is successful
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        assert role.name == self.role_data['name']
        assert role.created_by == 'me'  # TODO: Change to user.id
        assert role.id == 1

    def test_create_same_role_expected_exception(self, use_test_db, mocker):
        """
        Test that creating same role will raise exception
        :param use_test_db:
        :param mocker:
        :return:
        """
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        with pytest.raises(exceptions.RoleAlreadyExists):
            operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id

    def test_add_user_to_role_expected_success(self, use_test_db, mocker):
        user = operations.create_new_user(input_models.RegisterUserInputModel(**self.user_data))
        role = operations.create_role(self.role_data['name'], 'me')  # TODO: Change to user.id
        user_roles = user.roles
        operations.add_user_to_role(role_id=role.id, user_id=user.id, added_by='me')  # TODO: Change to user.id
        with db.connection.get_session() as session:
            users = session.query(models.User).all()
        assert len(user_roles) + 1 == len(users[0].roles)
        assert users[0].roles[0] == role


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
