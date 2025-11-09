from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command='/start',
            description='Начало работы.'
        ),
        BotCommand(
            command='/help',
            description='Описание функциональности'
        ),
        BotCommand(
            command='/rate',
            description='Оценить фильмы'
        ),
        BotCommand(
            command='/cancel_rate',
            description='Закончить оценивание'
        ),
        BotCommand(
            command='/recommend',
            description='Получить рекомендации'
        )
    ]
    await bot.set_my_commands(main_menu_commands)