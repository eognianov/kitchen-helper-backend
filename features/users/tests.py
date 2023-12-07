import pytest
import db.connection
from features.users.input_models import RegisterUserInputModel
from tests.fixtures import use_test_db
from features.users import operations
from features.users.models import User
from fastapi.testclient import TestClient
from api import app


class TestUserOperations:
    client = TestClient(app)

    def test_create_new_user_success(self, use_test_db, mocker):
        user_data = {
            'username': 'test_user',
            'email': '_test_example@abv.bg',
            'password': 'secure_password!2'
        }

        operations.create_new_user(RegisterUserInputModel(**user_data))
        with db.connection.get_session() as session:
            users = session.query(User).all()
        assert users[0].username == user_data['username']
        assert users[0].email == user_data['email']
        assert users[0].id == 1
