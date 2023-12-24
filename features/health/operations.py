from db.connection import get_engine
from sqlalchemy import exc as sqlalchemy_exc


def check_db_status() -> str:
    try:
        get_engine().connect()
        return "Working"
    except sqlalchemy_exc.DBAPIError as e:
        print(f"Database error: {e}")
        return "Not Working"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Not Working"
