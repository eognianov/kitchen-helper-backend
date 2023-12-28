"""Configuation module"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib
from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict
from enum import StrEnum, auto


_module_path = pathlib.Path(__file__).resolve()
ROOT_PATH = _module_path.parent
MEDIA_PATH = ROOT_PATH.joinpath('media')

_ENV_FILES_PATHS = (
    pathlib.Path(f'{ROOT_PATH}/.env.template'),
    pathlib.Path(f'{ROOT_PATH}/.env.dev'),
    pathlib.Path(f'{ROOT_PATH}/.env.prod'),
)


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES_PATHS,
        validate_default=True,
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='ignore',
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


class JwtToken(CustomBaseSettings):
    """JWT Token settings"""

    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    algorithm: str
    secret_key: str
    refresh_secret_key: str


class CorsSettings(CustomBaseSettings):
    """CORSMiddleware settings"""

    allow_origins: List[str]
    allow_methods: List[str]
    allow_headers: List[str]


class BrevoSettings(CustomBaseSettings):
    """Brevo settings"""

    email_api_key: str
    email_api_url: str
    email_sender: str
    email_from: str


class ConfirmationToken(CustomBaseSettings):
    """Email confirmation and password reset token"""

    email_token_expiration_minutes: int
    password_token_expiration_minutes: int


class ServerConfiguration(BaseModel):
    host: str
    port: int


class RabbitmqConfiguration(BaseModel):
    user: str
    password: str


class CelerySettings(BaseModel):
    """Cloudinary settings"""

    broker: str
    backend: str
    host: str
    port: int


class Config(CustomBaseSettings):
    """Base configurations"""

    context: ContextOptions = ContextOptions.DEV
    database: DbTypeOptions = DbTypeOptions.SQLITE
    sqlite: SqliteConfig
    postgres: PostgresConfig
    server: ServerConfiguration
    rabbitmq: RabbitmqConfiguration
    celery: CelerySettings

    @property
    def connection_string(self):
        if self.database == DbTypeOptions.POSTGRES:
            return self.postgres.connection_string
        return self.sqlite.connection_string

    @model_validator(mode='after')
    def validate_db_configuration(self):
        if self.database == DbTypeOptions.POSTGRES and not self.postgres.are_all_fields_populated:
            raise ValueError('You have selected postgres as database but did not provide its configuration')

    def get_broker_url(self) -> str:
        return (
            f"{self.celery.broker}{self.rabbitmq.user}:{self.rabbitmq.password}@{self.celery.host}:{self.celery.port}//"
        )


class Cloudinary(CustomBaseSettings):
    """Cloudinary settings"""

    cloud_name: str
    api_key: str
    api_secret: str


class AppUsers(CustomBaseSettings):
    users: List[Dict[str, str]]


class AppUsersRoles(CustomBaseSettings):
    role: str


class AppRecipeCategories(CustomBaseSettings):
    categories: List[str]
