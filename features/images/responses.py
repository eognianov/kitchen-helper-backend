from pydantic import BaseModel
from datetime import datetime

import configuration
from .constants import IMAGES_DIR
from pathlib import Path


class ImageResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    uploaded_on: datetime
    uploaded_by: int
    in_cloudinary: bool
    url: str = ''

    def model_post_init(self, __context):
        if not self.in_cloudinary:
            self.url = Path.joinpath(IMAGES_DIR, self.name).relative_to(configuration.ROOT_PATH)
        else:
            self.url = f"https://res.cloudinary.com/{configuration.Cloudinary().cloud_name}/image/upload/{self.name}"
