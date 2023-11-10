from pytest import fixture
from db import connection


@fixture()
def use_test_db(monkeypatch):
    monkeypatch.setattr(connection, 'CONNECTION_STRING', 'sqlite:///:memory:')
    monkeypatch.setattr(connection, 'get_engine', connection._get_test_engine)
    yield
