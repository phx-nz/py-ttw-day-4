__all__ = ["ConfigService", "Env"]

from enum import StrEnum, auto
from os import getenv
from typing import Any, ClassVar, Self, TYPE_CHECKING

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from services.base import BaseService


class Env(StrEnum):
    """
    Possible values for the ``PY_ENV`` environment variable.
    See ``.env`` for more information.
    """

    development = auto()
    production = auto()
    test = auto()


def get_env_name() -> Env:
    """
    Returns the environment name, used to decide which ``.env.*`` file to load.
    """
    return Env[getenv("PY_ENV", Env.development)]


class BaseConfig(BaseModel):
    """
    Provides runtime configuration values (e.g., environment vars) for the application.
    """

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_database: str
    db_protocol: str

    @property
    def db_connection_string(self) -> str:
        """
        Assembles the DB connection string for :py:func:`sqlalchemy.create_engine`.

        :see: https://docs.sqlalchemy.org/en/20/tutorial/engine.html
        """
        return (
            # If SQLite, assume in-memory database.
            f"{self.db_protocol}"
            if self.db_protocol.startswith("sqlite")
            else f"{self.db_protocol}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"
        )


class AppConfig(BaseConfig, BaseSettings):
    """
    Loads configuration values for the app from environment variables.

    :see: https://fastapi.tiangolo.com/advanced/settings/
    """

    env: ClassVar[Env] = get_env_name()

    model_config = SettingsConfigDict(
        # Conventionally, env vars are specified in SHOUTING_SNAKE_CASE, but we want to
        # access them using regular snake_case in our code.
        # :see: https://github.com/pydantic/pydantic/issues/1105
        case_sensitive=False,
        # Load values from a ``.env.*`` file.
        # Note that environment variables always take precedence.
        # :see: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#dotenv-env-support
        env_file=f".env.{env}",
    )

    @property
    def is_production(self) -> bool:
        """
        :returns: whether we are operating in a production environment.
        """
        return self.env == Env.production

    @property
    def is_development(self) -> bool:
        """
        :returns: whether we are operating in a development environment.
        """
        return self.env == Env.development

    @property
    def is_test(self) -> bool:
        """
        :returns: whether we are operating in a test environment.
        """
        return self.env == Env.test


class TestConfig(BaseSettings):
    """
    Overrides configuration values for unit tests.
    """

    __test__ = False

    env: ClassVar[Env] = Env.test
    db_connection_string: ClassVar[str] = "sqlite+aiosqlite://"

    is_production: ClassVar[bool] = False
    is_development: ClassVar[bool] = False
    is_test: ClassVar[bool] = True


if TYPE_CHECKING:
    # Teach IDE how to interpret :py:meth:`ConfigService.__getattr__`.
    class ConfigService(BaseConfig):
        pass

else:

    class ConfigService(BaseService):
        """
        Provides application configuration as a service.
        """

        provides = "config"

        @classmethod
        def factory(cls) -> Self:
            return ConfigService(
                TestConfig() if get_env_name() == Env.test else AppConfig()
            )

        def __init__(self, config: BaseConfig):
            super().__init__()
            self.config = config

        def __getattr__(self, item: str) -> Any:
            """
            Returns the config value for the specified key.
            """
            return getattr(self.config, item)
