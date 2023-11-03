from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: list[dict]
