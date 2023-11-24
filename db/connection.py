"""DB connection module"""
import sqlalchemy
import sqlalchemy.orm
import configuration

config = configuration.Config()

CONNECTION_STRING = config.connection_string


def _get_test_engine() -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(CONNECTION_STRING, echo=False, connect_args={"check_same_thread": False},
                                    poolclass=sqlalchemy.StaticPool)


def get_engine() -> sqlalchemy.Engine:
    """
    Return engine
    :return:
    """

    echo = config.context == configuration.ContextOptions.DEV
    if config.database == configuration.DbTypeOptions.SQLITE and config.sqlite.is_in_memory:
        return _get_test_engine()
    return sqlalchemy.create_engine(CONNECTION_STRING, echo=echo)


def get_connection(engine: sqlalchemy.Engine = None) -> sqlalchemy.Connection:
    """
    Get connection

    :param engine:
    :return:
    """

    if not engine:
        engine = get_engine()
    return engine.connect()


def get_session(engine: sqlalchemy.Engine = None) -> sqlalchemy.orm.Session:
    """
    Get session
    :param engine:
    :return:
    """

    if not engine:
        engine = get_engine()
    return sqlalchemy.orm.Session(bind=engine, autocommit=False, autoflush=False)
