from dataclasses import asdict

from config import Config, load_config
from api import ASRApi, FireworksApi, NexaraApi

from gui import run_gui_app


def main():
    config: Config = load_config()
    fw_api: ASRApi = FireworksApi(**asdict(config.fw_api_config))
    nexara_api: ASRApi = NexaraApi(**asdict(config.nexara_api_config))

    run_gui_app(fw_api, nexara_api)


if __name__ == "__main__":
    main()
