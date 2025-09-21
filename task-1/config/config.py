from dataclasses import dataclass, field
from environs import Env


@dataclass
class ApiConfig:
    name: str = field(repr=True)
    url: str = field(repr=True)
    api_key: str = field(repr=True)


@dataclass
class Config:
    fw_api_config: ApiConfig = field(repr=True)
    nexara_api_config: ApiConfig = field(repr=True)


def load_config() -> Config:
    env: Env = Env()
    env.read_env()

    return Config(
        fw_api_config=ApiConfig(
            name="Fireworks",
            url="https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions",
            api_key=env("FIREWORKS_API_KEY"),
        ),
        nexara_api_config=ApiConfig(
            name="Nexara",
            url="https://api.nexara.ru/api/v1/audio/transcriptions",
            api_key=env("NEXARA_API_KEY"),
        ),
    )
