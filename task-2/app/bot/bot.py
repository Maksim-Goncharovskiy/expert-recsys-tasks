import asyncio
from aiogram import Bot, Dispatcher
from config import Config
from app.bot.handlers import command_router, callback_router, message_router


async def main(config: Config):
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    dp.include_router(command_router)
    dp.include_router(callback_router)
    dp.include_router(message_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
