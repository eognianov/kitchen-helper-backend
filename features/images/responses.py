from pydantic import BaseModel
from datetime import datetime


class ImageResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    uploaded_on: datetime
    uploaded_by: int
    in_cloudinary: bool
