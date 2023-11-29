from pytest import fixture
from db import connection
from features import DbBaseModel


@fixture
def use_test_db(monkeypatch, mocker):
    monkeypatch.setattr(connection, "CONNECTION_STRING", f"sqlite:///:memory:")
    test_engine = connection._get_test_engine()
    mocker.patch("db.connection.get_engine", return_value=test_engine)
    DbBaseModel.metadata.create_all(bind=connection.get_engine())
