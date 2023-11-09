from .models import Image
from PIL import Image as PImage
from db.connection import get_session
from datetime import datetime
from fastapi import UploadFile
from httpx import AsyncClient, HTTPStatusError, RequestError
import os
import aiofiles
import secrets

from configuration import Config

SQLALCHEMY_DATABASE_URL = Config().connection_string


def generate_id() -> str:
    return secrets.token_hex(16)


def construct_url(file_name: str) -> str:
    return "http://127.0.0.1:8000/" + "uploads/" + str(file_name)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, 'uploads')


async def save_file_to_disk(file_path: str, content: bytes):
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)


async def get_image_dimensions(file_path: str):
    with PImage.open(file_path) as img:
        return img.size


def generate_filename(file_name: str) -> str:
    file_extension = os.path.splitext(file_name)[1]
    return secrets.token_hex(8) + file_extension


async def save_metadata_to_db(image_metadata):
    session = get_session()
    new_image = Image(**image_metadata)
    try:
        session.add(new_image)
        session.commit()
        session.refresh(new_image)
        return new_image.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


async def process_and_store_image(file_name: str, content: bytes, uploader: str = "test_uploader"):
    unique_filename = generate_filename(file_name)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    await save_file_to_disk(file_path, content)
    width, height = await get_image_dimensions(file_path)

    image_metadata = {
        'name': unique_filename,
        'storage_location': file_path,
        'width': width,
        'height': height,
        'uploaded_on': datetime.now(),
        'uploaded_by': uploader
    }

    image_id = await save_metadata_to_db(image_metadata)
    image_metadata["id"] = image_id
    return image_metadata


# Main functions
async def is_reachable_url(url: str) -> bool:
    async with AsyncClient() as client:
        try:
            response = await client.head(url)
            response.raise_for_status()
            return True
        except HTTPStatusError:
            return False
        except RequestError:
            return False


async def download_image_from_url(url: str) -> bytes:
    if not await is_reachable_url(url):
        raise ValueError("The URL provided is not reachable.")

    async with AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        if 'image' not in response.headers.get('Content-Type', ''):
            raise ValueError("URL does not point to a valid image file.")

        return response.content


async def save_image_from_url(url: str, uploader: str):
    image_content = await download_image_from_url(url)
    file_name = url.split('/')[-1]
    return await process_and_store_image(file_name, image_content, uploader)


async def save_image_from_file(file: UploadFile, uploader: str):
    content = await file.read()
    return await process_and_store_image(file.filename, content, uploader)
