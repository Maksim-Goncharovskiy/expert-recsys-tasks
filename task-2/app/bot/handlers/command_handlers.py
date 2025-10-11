import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.lexicon.lexicon import LEXICON_RU
from app.bot.keyboards import model_keyboard


logger = logging.getLogger(__name__)


command_router = Router()


@command_router.message(Command(commands=["start"]))
async def say_hello(message: Message):
    logger.info(f"Пользователь {message.from_user.id} выполнил команду /start. Отправка ответа...")

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(LEXICON_RU["/start"])

    logger.info(f"Ответ успешно отправлен")


@command_router.message(Command(commands=["help"]))
async def provide_help(message: Message):
    """
    Обработка команды /help от пользователя.
    Даёт описание функционала бота.
    """
    logger.info(f"Пользователь {message.from_user.id} выполнил команду /help. Отправка ответа...")

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(LEXICON_RU["/help"])

    logger.info("Ответ успешно отправлен")


@command_router.message(Command(commands=["model"]))
async def choose_model(message: Message):
    """
    Обработка команды /model от пользователя. 
    Отправляет пользователю клавиатуру с кнопками выбора модели.
    """
    logger.info(f"Пользователь {message.from_user.id} выполнил команду /model")

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(LEXICON_RU["/model"], reply_markup=model_keyboard)

    logger.info(f"Ответ успешно отправлен")