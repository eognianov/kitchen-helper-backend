from pydantic import BaseModel
from datetime import datetime
import features.images.operations


class ImageResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    uploaded_on: datetime
    uploaded_by: int
    in_cloudinary: bool
    url: str = ""

    def model_post_init(self, __context):
        _url = features.images.operations.generate_image_url(self.name, self.in_cloudinary)
        self.url = _url
