from dataclasses import dataclass, field
from environs import Env



@dataclass
class BotConfig:
    token: str = field(repr=False)


@dataclass
class DatabaseConfig:
    path: str = field(repr=True)
    user_table: str = field(repr=True)
    movie_table: str = field(repr=True)


@dataclass
class Config:
    bot: BotConfig = field(repr=True)
    db: DatabaseConfig = field(repr=True)


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            token=env("BOT_TOKEN")
        ),
        db=DatabaseConfig(
            path=env("DATABASE"),
            user_table=env("USERS_TABLE"),
            movie_table=env("MOVIES_TABLE")
        )
    )


CONFIG = load_config()