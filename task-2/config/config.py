from dataclasses import dataclass, field
from environs import Env



@dataclass
class BotConfig:
    token: str = field(repr=False)


@dataclass
class RedisConfig:
    host: str = field(repr=True)
    port: int = field(repr=True)


@dataclass
class DatabaseConfig:
    path: str = field(repr=True)
    schema_path: str = field(repr=True)


@dataclass
class LLMApiConfig:
    api_key: str = field(repr=False)
    url: str = field(repr=True)


@dataclass
class Config:
    bot: BotConfig = field(repr=True)
    redis: RedisConfig = field(repr=True)
    db: DatabaseConfig = field(repr=True)
    llm_api: LLMApiConfig = field(repr=True)


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            token=env("BOT_TOKEN")
        ),
        redis=RedisConfig(
            host=env("REDIS_HOST"),
            port=env("REDIS_PORT")
        ),
        db=DatabaseConfig(
            path=env("DB_PATH"),
            schema_path=env("DB_SCHEMA_PATH")
        ),
        llm_api=LLMApiConfig(
            api_key=env("API_KEY"),
            url=env("URL")
        )
    )


CONFIG = load_config()