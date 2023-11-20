import io
import uuid
from pathlib import Path

import db.connection
from .constants import IMAGES_DIR
from .models import Image
from .exceptions import InvalidCreationInputException, ImageUrlIsNotReachable, ImageNotFoundException
from PIL import Image as PImage
from httpx import AsyncClient, HTTPStatusError, RequestError
import aiofiles
import cloudinary.uploader
import configuration


async def _save_file_to_disk(file_path: str, content: bytes):
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)


async def _get_image_metadata(image_content: io.BytesIO):
    with PImage.open(image_content) as img:
        return img.size, img.format.lower()


def upload_image_to_cloud(content: bytes, image_name: str, uploader: str) -> bool:
    cloudinary.config(
        **configuration.Cloudinary().model_dump()
    )
    response = cloudinary.uploader.upload(
        content,
        public_id=image_name.split('.')[0],
        context=f"uploader={uploader}"
    )
    return bool(response.get('secure_url'))


async def _download_image_from_url(url: str) -> bytes:
    """
    Get image from url

    :param url:
    :return:
    """

    async with AsyncClient() as client:
        try:

            response = await client.get(url)
            response.raise_for_status()

            if 'image' not in response.headers.get('Content-Type', ''):
                raise ValueError("URL does not point to a valid image file.")

            return response.content
        except HTTPStatusError:
            raise ImageUrlIsNotReachable
        except RequestError:
            raise ImageUrlIsNotReachable


async def add_image(url: str = None, image: bytes = None, added_by: int = '1'):
    """
    Add image

    :param url:
    :param image:
    :return:
    """

    if not (url or image) or (url and image):
        raise InvalidCreationInputException

    if url:
        image = await _download_image_from_url(url)

    size, extension = await _get_image_metadata(io.BytesIO(image))
    file_name = str(uuid.uuid4()) + f'.{extension}'
    file_path = Path.joinpath(IMAGES_DIR, file_name)
    await _save_file_to_disk(file_path, image)

    image_metadata = {
        'name': file_name,
        'width': size[0],
        'height': size[0],
        'uploaded_by': added_by
    }

    with db.connection.get_session() as session:
        image_db = Image(**image_metadata)
        session.add(image_db)
        session.commit()
        session.refresh(image_db)

    return image_db


async def get_image(image_id: int):
    """
    Get image
    :param image_id:
    :return:
    """

    with db.connection.get_session() as session:
        image = session.query(Image).where(Image.id == image_id).first()

        if not image:
            raise ImageNotFoundException
        return image


async def get_images():
    """
    Get images
    :return:
    """
    with db.connection.get_session() as session:
        return session.query(Image).all()
