import fastapi
from . import responses

router = fastapi.APIRouter()


@router.get('/', response_model=responses.BaseHealthResponse)
def api_health():
    """API health"""
    return responses.BaseHealthResponse(status_code=fastapi.status.HTTP_200_OK, text="API is healthy")