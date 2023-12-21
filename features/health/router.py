import fastapi
from sqlalchemy import exc as sqlalchemy_exc

from db.connection import get_engine, get_connection
from . import responses

router = fastapi.APIRouter()


def check_db_status() -> str:
    try:
        engine = get_engine()
        with get_connection(engine) as connection:
            connection.execute('SELECT 1')
        return "Working"
    except sqlalchemy_exc.DBAPIError as e:
        print(f"Database error: {e}")
        return "Not Working"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Not Working"


@router.get('/', response_model=responses.BaseHealthResponse)
def api_health():
    """API health"""
    db_status = check_db_status()

    return responses.BaseHealthResponse(
        status_code=fastapi.status.HTTP_200_OK,
        text="API is healthy",
        db_status=db_status
    )
