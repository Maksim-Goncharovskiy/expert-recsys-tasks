import logging
import asyncio
from config import Config, load_config
from app.bot.bot import main



if __name__ == "__main__":
    try:
        config: Config = load_config()
    except Exception as err:
        logging.error(f"Ошибка при чтении конфигурации: {err}")
    else:
        asyncio.run(main=main(config))