import logging
import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from app.bot.lexicon import LEXICON_RU
from app.bot.fsm import UserStates
from app.database import CsvMovieDatabaseManager, CsvDatabaseConfig
from app.recommendation import PirsonUCF
from app.bot.keyboards import rating_keyboard
from config import CONFIG


logger = logging.getLogger(__name__)


command_router = Router()


db_manager = CsvMovieDatabaseManager(config=CsvDatabaseConfig(
    db_path=CONFIG.db.path,
    user_table=CONFIG.db.user_table,
    movie_table=CONFIG.db.movie_table))


recsys = PirsonUCF(db_manager)


@command_router.message(Command(commands=["start"]), StateFilter(default_state))
async def say_hello(message: Message):
    logger.info(f"Пользователь {message.from_user.id} выполнил команду /start. Отправка ответа...")

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(LEXICON_RU["commands"]["start"])

    logger.info(f"Ответ успешно отправлен")



@command_router.message(Command(commands=["help"]), StateFilter(default_state))
async def provide_help(message: Message):
    """
    Обработка команды /help от пользователя.
    Даёт описание функционала бота.
    """
    logger.info(f"Пользователь {message.from_user.id} выполнил команду /help. Отправка ответа...")

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(LEXICON_RU["commands"]["help"])

    logger.info("Ответ успешно отправлен")



@command_router.message(Command(commands=["rate"]), StateFilter(default_state))
async def start_rating(message: Message, state: FSMContext):
    """Запуск процедуры оценивания фильмов"""
    await state.set_state(UserStates.rate)

    user_id = message.from_user.id
    movies = db_manager.get_user_new_movies(user_id=user_id)

    movie = random.choice(list(movies))

    await state.update_data(movie=movie)
    await message.answer(f"Оцените фильм: '{movie}'", reply_markup=rating_keyboard)



@command_router.message(Command(commands=["cancel_rate"]), StateFilter(UserStates.rate))
async def cancel_rating(message: Message, state: FSMContext):
    """Выход из процедуры оценивания"""
    await state.clear()
    await message.answer(LEXICON_RU["commands"]["rate_finished"])



@command_router.message(Command(commands=["recommend"]), StateFilter(default_state))
async def get_recommendations(message: Message, state: FSMContext):
    """Получение рекомендаций"""
    user_id = message.from_user.id

    recommendations = recsys.provide_recommendation(user_id=user_id)

    answer = "Возможно вам понравится:\n"
    for idx, movie in enumerate(recommendations):
        answer += f"{idx + 1}. {movie}\n"
        
    await message.answer(answer)
