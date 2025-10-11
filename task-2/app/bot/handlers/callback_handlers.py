from redis.asyncio import Redis
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from app.bot.lexicon.lexicon import LEXICON_RU
from app.bot.keyboards import model_keyboard
from app.bot.lexicon import LEXICON_RU
from config import load_config, Config


CONFIG: Config = load_config()

REDIS = Redis(host=CONFIG.redis.host, port=CONFIG.redis.port)

callback_router = Router()


@callback_router.callback_query(F.data == 'qwen3-coder')
@callback_router.callback_query(F.data == 'gpt-oss-120b')
async def process_change_model(callback: CallbackQuery):
    await REDIS.set(f"{callback.from_user.id}", f"{callback.data}")
    await callback.message.answer(LEXICON_RU["model_changed"].format(model=callback.data))