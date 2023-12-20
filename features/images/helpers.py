from pathlib import Path

import configuration
from features.images.constants import IMAGES_DIR


def read_image_as_bytes(image: str) -> tuple:
    """
    Reads an image and returns a bytes and image's file path
    :param image:
    :return:
    """
    file_path = Path.joinpath(IMAGES_DIR, image).relative_to(configuration.ROOT_PATH)
    with open(file_path, "rb") as file:
        image_bytes = file.read()
    return image_bytes, file_path
