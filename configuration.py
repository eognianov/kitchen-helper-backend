"""Configuation module"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib
from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict
from enum import StrEnum, auto
from celery import Celery


_module_path = pathlib.Path(__file__).resolve()
ROOT_PATH = _module_path.parent
MEDIA_PATH = ROOT_PATH.joinpath("media")
ROOT_PATH.joinpath("cache").mkdir(exist_ok=True)
CACHE_PATH = ROOT_PATH.joinpath("cache")

_ENV_FILES_PATHS = (
    pathlib.Path(f"{ROOT_PATH}/.env.template"),
    pathlib.Path(f"{ROOT_PATH}/.env.dev"),
    pathlib.Path(f"{ROOT_PATH}/.env.prod"),
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

    broker: Optional[str] = "pyamqp://"
    backend: Optional[str] = "rpc://"
    host: Optional[str] = "localhost"
    port: Optional[int] = 5672
    task_serializer: Optional[str] = "json"
    result_serializer: Optional[str] = "json"
    accept_content: Optional[List[str]] = ["json"]
    timezone: Optional[str] = "UTC"
    enable_utc: Optional[bool] = True
    broker_connection_retry_on_startup: Optional[bool] = True
    include_tasks: List[str]
    beat_schedule: List[str]


class Config(CustomBaseSettings):
    """Base configurations"""

    context: ContextOptions = ContextOptions.DEV
    database: DbTypeOptions = DbTypeOptions.SQLITE
    log_queries: bool
    sqlite: SqliteConfig
    postgres: PostgresConfig
    server: ServerConfiguration
    rabbitmq: RabbitmqConfiguration
    celery: CelerySettings
    users_grpc_server_host: str

    @property
    def running_on_dev(self) -> bool:
        """Check if app is running on dev"""
        return self.context == ContextOptions.DEV

    @property
    def connection_string(self):
        if self.database == DbTypeOptions.POSTGRES:
            return self.postgres.connection_string
        return self.sqlite.connection_string

    @model_validator(mode="after")
    def validate_db_configuration(self):
        if self.database == DbTypeOptions.POSTGRES and not self.postgres.are_all_fields_populated:
            raise ValueError("You have selected postgres as database but did not provide its configuration")

    def get_celery_broker_url(self) -> str:
        return (
            f"{self.celery.broker}{self.rabbitmq.user}:{self.rabbitmq.password}@{self.celery.host}:{self.celery.port}//"
        )

    def get_celery_beat_schedule(self):
        beat_schedule = {}
        for task in self.celery.beat_schedule:
            task_path, task_schedule = task.split("/")
            beat_schedule[task_path.split(".")[-1]] = {
                "task": task_path,
                "schedule": int(task_schedule),
            }
        return beat_schedule

    def get_broker_url(self) -> str:
        return (
            f"{self.celery.broker}{self.rabbitmq.user}:{self.rabbitmq.password}@{self.celery.host}:{self.celery.port}//"
        )


class Cloudinary(CustomBaseSettings):
    """Cloudinary settings"""

    cloud_name: str
    api_key: str
    api_secret: str


class OpenAi(CustomBaseSettings):
    chatgpt_api_key: str


class AppUsers(CustomBaseSettings):
    users: List[Dict[str, str]]


class AppUsersRoles(CustomBaseSettings):
    role: str


class AppRecipeCategories(CustomBaseSettings):
    categories: List[str]


""" Celery configuration"""
config = Config()

celery = Celery(
    __name__,
    broker=config.get_celery_broker_url(),
    backend=config.celery.backend,
    task_serializer=config.celery.task_serializer,
    result_serializer=config.celery.result_serializer,
    accept_content=config.celery.accept_content,
    timezone=config.celery.timezone,
    enable_utc=config.celery.enable_utc,
    broker_connection_retry_on_startup=config.celery.broker_connection_retry_on_startup,
    include=config.celery.include_tasks,
    beat_schedule=config.get_celery_beat_schedule(),
)
