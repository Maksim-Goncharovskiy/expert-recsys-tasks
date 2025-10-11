from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.lexicon.lexicon import LEXICON_RU


base_router = Router()


@base_router.message(Command(commands=["start"]))
async def say_hello(message: Message):
    await message.answer(LEXICON_RU["/start"])


@base_router.message(Command(commands=["help"]))
async def provide_help(message: Message):
    await message.answer(LEXICON_RU["/help"])