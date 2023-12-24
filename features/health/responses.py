"""Health responses"""
import pydantic


class BaseHealthResponse(pydantic.BaseModel):
    """Base health response"""
    status_code: int
    text: str
    db_status: str

