from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.lexicon.lexicon import LEXICON_RU
from app.bot.keyboards import model_keyboard


command_router = Router()


@command_router.message(Command(commands=["start"]))
async def say_hello(message: Message):
    await message.answer(LEXICON_RU["/start"])


@command_router.message(Command(commands=["help"]))
async def provide_help(message: Message):
    await message.answer(LEXICON_RU["/help"])


@command_router.message(Command(commands=["model"]))
async def choose_model(message: Message):
    await message.answer(LEXICON_RU["/model"], reply_markup=model_keyboard)