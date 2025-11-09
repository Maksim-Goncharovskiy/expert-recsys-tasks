import os
import sys
import logging
import asyncio
from config import Config, load_config
from app.bot.bot import main


LOG_FILE = "logs/bot.log"


def setup_logging():
    """Выполняет настройку логгирования"""

    # Создаем директорию для логов, если её нет
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    user_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    user_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    user_handler.setFormatter(user_formatter)

    # Настройка логгера
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            user_handler,
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logging()


if __name__ == "__main__":
    try:
        config: Config = load_config()
    except Exception as err:
        pass 
    else:
        asyncio.run(main=main(config))