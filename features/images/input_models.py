import fastapi
from pydantic import BaseModel, HttpUrl, constr


class ImageFromFile(BaseModel):
    pass


class ImageFromUrl(BaseModel):
    url: str
