from pydantic import BaseModel, HttpUrl


class ImageFromFile(BaseModel):
    pass


class ImageFromUrl(BaseModel):
    url: str
