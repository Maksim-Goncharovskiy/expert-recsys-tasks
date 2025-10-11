import asyncio
from aiogram import Bot, Dispatcher
from config import Config, load_config
from app.bot.handlers.base_handlers import base_router


async def main(config: Config):
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    dp.include_router(base_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
