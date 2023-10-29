"""Configuation module"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib

from enum import StrEnum, auto

_module_path = pathlib.Path(__file__).resolve()
ROOT_PATH = _module_path.parent

_ENV_FILES_PATHS = (
    pathlib.Path(f'{ROOT_PATH}/.env.template'),
    pathlib.Path(f'{ROOT_PATH}/.env.dev'),
    pathlib.Path(f'{ROOT_PATH}/.env.prod'),
)


class ContextOptions(StrEnum):
    PROD = auto()
    DEV = auto()
    TEST = auto()

    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if member == value:
                return member
        return None


class Config(BaseSettings):
    context: ContextOptions = 'dev'

    model_config = SettingsConfigDict(env_file=_ENV_FILES_PATHS, validate_default=True, case_sensitive=False)