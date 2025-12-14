import random
import logging
from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from app.bot.lexicon import LEXICON_RU
from app.bot.fsm import UserStates
from app.database import db_manager
from app.recsys import recsys
from app.bot.keyboards import rating_keyboard
from config import CONFIG


logger = logging.getLogger(__name__)


callback_router = Router()



@callback_router.callback_query(F.data.in_({'1', '2', '3', '4', '5'}), StateFilter(UserStates.rate))
async def process_rate(callback: CallbackQuery, state: FSMContext):
    """Обработка получения оценки для фильма"""
    user_id = callback.from_user.id 

    rate = int(callback.data) 

    data = await state.get_data()

    movie = data.get('movie', None)

    status = db_manager.set_user_movie_rate(user_id, movie, rate)
    if not(status):
        logger.error("Ошибка записи оценки пользователя.")

    movies = db_manager.get_user_new_movies(user_id=user_id)

    movie = random.choice(list(movies))

    await state.update_data(movie=movie)

    await callback.message.edit_text(f"Оцените фильм: '{movie}'")
    await callback.message.edit_reply_markup(reply_markup=rating_keyboard)



@callback_router.callback_query(F.data=="finish_rating", StateFilter(UserStates.rate))
async def process_rate(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку 'закончить оценивание' """
    await state.clear()
    recsys.finetune_user(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(LEXICON_RU["commands"]["rate_finished"])