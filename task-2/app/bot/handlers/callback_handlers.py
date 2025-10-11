import logging
from redis.asyncio import Redis
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from app.bot.lexicon import LEXICON_RU
from config import load_config, Config


logger = logging.getLogger(__name__)


CONFIG: Config = load_config()

REDIS = Redis(host=CONFIG.redis.host, port=CONFIG.redis.port)

callback_router = Router()


@callback_router.callback_query(F.data == 'qwen3-coder')
@callback_router.callback_query(F.data == 'gpt-oss-120b')
async def process_change_model(callback: CallbackQuery):
    """
    Обработка нажатия пользователем кнопки выбора модели.
    Сохраняет выбранную пользователем модель в redis-хранилище. В качестве ключа - id пользователя.
    """
    logger.info(f"Пользователь {callback.from_user.id} выбрал модель {callback.data}. Запись в redis хранилище...")

    await REDIS.set(f"{callback.from_user.id}", f"{callback.data}")

    logger.info(f"Запись в redis успешно завершена. Отправка сообщения пользователю.")

    await callback.message.answer(LEXICON_RU["model_changed"].format(model=callback.data))

    logger.info(f"Ответ успешно отправлен")