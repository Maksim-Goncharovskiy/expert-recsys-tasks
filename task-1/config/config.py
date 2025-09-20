import dataclasses
import environs


@dataclasses.dataclass
class Config:
    fw_api_key: str
    nexara_api_key: str


def load_config() -> Config:
    env = environs.Env()
    env.read_env()

    return Config(
        fw_api_key=env("FIREWORKS_API_KEY"),
        nexara_api_key=env("NEXARA_API_KEY")
    )