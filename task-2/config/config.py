from dataclasses import dataclass, field
from environs import Env


@dataclass
class BotConfig:
    token: str = field(repr=True)
    allowed_users: list[int] = field(repr=True)


@dataclass
class DatabaseConfig:
    path: str = field(repr=True)


@dataclass
class LLMApiConfig:
    api_key: str = field(repr=True)
    url: str = field(repr=True)


@dataclass
class Config:
    bot: BotConfig = field(repr=True)
    db: DatabaseConfig = field(repr=True)
    llm_api: LLMApiConfig = field(repr=True)


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            token=env("BOT_TOKEN"),
            allowed_users=list(map(int, env.list("ALLOWED_USERS")))
        ),
        db=DatabaseConfig(
            path=env("DB_PATH")
        ),
        llm_api=LLMApiConfig(
            api_key=env("API_KEY"),
            url=env("URL")
        )
    )