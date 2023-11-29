"""Configuation module"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib
from pydantic import BaseModel, model_validator, Field
from typing import Optional, List
from enum import StrEnum, auto
from dotenv import load_dotenv

load_dotenv('.env.dev')

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

    file_name: Optional[str] = None

    @property
    def connection_string(self) -> str:
        """Get connection string"""
        return f"sqlite:///{self.file_name if self.file_name else ':memory:'}"

    @property
    def is_in_memory(self) -> bool:
        """Check if sqlite is running in memory"""
        return not self.file_name


class PostgresConfig(BaseModel):
    """PostgreSQL configuration"""

    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

    @property
    def connection_string(self) -> str:
        """Get connection string"""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def are_all_fields_populated(self):
        """Check if all fields are populated"""
        return self.host and self.port and self.user and self.password and self.database


class JwtToken(BaseModel):
    """JWT Token options"""
    access_token_expire_minutes: int = os.getenv('jwt_access_token_expire_minutes')
    refresh_token_expire_minutes: int = os.getenv('jwt_refresh_token_expire_minutes')
    algorithm: str = os.getenv('jwt_algorithm')
    secret_key: str = os.getenv('jwt_secret_key')
    refresh_secret_key: str = os.getenv('jwt_refresh_secret_key')


class CorsSettings(BaseModel):
    """CORSMiddleware options"""
    allow_origins: List[str] = os.getenv('cors__allow_origins', '').split(' ')
    allow_methods: List[str] = os.getenv('cors__allow_methods', '').split(' ')
    allow_headers: List[str] = os.getenv('cors__allow_headers', '').split(' ')


class SendGrid(BaseModel):
    """SendGrid options"""
    send_grid_api_key: str = os.getenv('send_grid_api_key')


class ConfirmationToken(BaseModel):
    """Email confirmation and password reset token"""
    email_token_expiration: int = int(os.getenv('email_token_expiration_minutes'))
    password_token_expiration: int = int(os.getenv('password_token_expiration_minutes'))


class ServerConfiguration(BaseModel):
    host: str = os.getenv('host')
    port: str = os.getenv('port')


class Config(BaseSettings):
    """Base configurations"""

    context: ContextOptions = ContextOptions.DEV
    database: DbTypeOptions = DbTypeOptions.SQLITE
    sqlite: SqliteConfig
    postgres: PostgresConfig
    server: ServerConfiguration



    @property
    def connection_string(self):
        if self.database == DbTypeOptions.POSTGRES:
            return self.postgres.connection_string
        return self.sqlite.connection_string

    model_config = SettingsConfigDict(env_file=_ENV_FILES_PATHS, validate_default=True,
                                      case_sensitive=False, env_nested_delimiter='__', extra='ignore')

    @model_validator(mode='after')
    def validate_db_configuration(self):
        if self.database == DbTypeOptions.POSTGRES and not self.postgres.are_all_fields_populated:
            raise ValueError('You have selected postgres as database but did not provide its configuration')


class Cloudinary(BaseSettings):
    """Cloudinary settings"""

    cloud_name: str = Field(alias='cloudinary__cloud_name')
    api_key: str = Field(alias='cloudinary__api_key')
    api_secret: str = Field(alias='cloudinary__api_secret')

    model_config = SettingsConfigDict(env_file=_ENV_FILES_PATHS, validate_default=True,
                                      case_sensitive=False, env_nested_delimiter='__', extra='ignore')