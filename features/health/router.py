import fastapi
from .operations import check_db_status
from . import responses

router = fastapi.APIRouter()


@router.get('/', response_model=responses.BaseHealthResponse)
def api_health():
    """API health"""
    db_status = check_db_status()

    return responses.BaseHealthResponse(
        status_code=fastapi.status.HTTP_200_OK,
        text="API is healthy",
        db_status=db_status
    )
