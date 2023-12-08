import pytest
import db.connection
from features.users.input_models import RegisterUserInputModel
from tests.fixtures import use_test_db
from features.users import operations
from features.users.models import User
from fastapi.testclient import TestClient
from api import app
import configuration


class TestUserOperations:
    client = TestClient(app)
    user_data = {
        'username': 'test_user',
        'email': '_test_example@abv.bg',
        'password': 'secure_password!2'
    }

    def test_create_new_user_success(self, use_test_db, mocker):

        operations.create_new_user(RegisterUserInputModel(**self.user_data))
        with db.connection.get_session() as session:
            users = session.query(User).all()
        assert users[0].username == self.user_data['username']
        assert users[0].email == self.user_data['email']
        assert users[0].id == 1

    def test_signin_user_success(self, use_test_db, mocker):
        operations.create_new_user(RegisterUserInputModel(**self.user_data))
        config = configuration.Config()
        print(config.jwt.algorithm)
        token, token_type = operations.signin_user(self.user_data['username'], self.user_data['password'])
        assert token_type == 'jwt access token'
