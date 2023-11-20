"""Images feature constants"""
from pathlib import Path
import configuration

IMAGES_DIR = Path.joinpath(configuration.ROOT_PATH, 'media/images')
IMAGES_DIR.mkdir(exist_ok=True, parents=True)