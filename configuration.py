"""Configuation module"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib
from pydantic import BaseModel, Field
from typing import Optional
from enum import StrEnum, auto

_module_path = pathlib.Path(__file__).resolve()
ROOT_PATH = _module_path.parent

_ENV_FILES_PATHS = (
    pathlib.Path(f'{ROOT_PATH}/.env.template'),
    pathlib.Path(f'{ROOT_PATH}/.env.dev'),
    pathlib.Path(f'{ROOT_PATH}/.env.prod'),
)


class CaseInsensitiveEnum(StrEnum):
    """Case insensitive enum"""
    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if member == value:
                return member
        return None


class ContextOptions(CaseInsensitiveEnum):
    """Context options"""
    PROD = auto()
    DEV = auto()
    TEST = auto()


class DbTypeOptions(CaseInsensitiveEnum):
    """DB type options"""
    SQLITE = auto()
    POSTGRES = auto()


class SqliteConfig(BaseModel):
    """SQLite configuration"""

    file_name: Optional[str]

    @property
    def connection_string(self) -> str:
        return f"sqlite:///{self.file_name if self.file_name else ':memory:'}"


class Config(BaseSettings):
    """Base configurations"""

    context: ContextOptions = ContextOptions.DEV
    database: DbTypeOptions = DbTypeOptions.SQLITE
    sqlite: SqliteConfig

    model_config = SettingsConfigDict(env_file=_ENV_FILES_PATHS, validate_default=True, case_sensitive=False, env_nested_delimiter='__')
