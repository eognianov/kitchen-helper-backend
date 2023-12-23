from pytest import fixture

import common.authentication
from db import connection
from features import DbBaseModel
from common.authentication import AuthenticatedUser


@fixture
def use_test_db(monkeypatch, mocker):
    monkeypatch.setattr(connection, "CONNECTION_STRING", f"sqlite:///:memory:")
    test_engine = connection._get_test_engine()
    mocker.patch("db.connection.get_engine", return_value=test_engine)
    DbBaseModel.metadata.create_all(bind=connection.get_engine())


@fixture
def admin(mocker):
    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "roles": [1]})
    yield


@fixture
def user(mocker):
    mocker.patch("jose.jwt.decode", return_value={"sub": "1"})
    yield common.authentication.AuthenticatedUser(id=1)
