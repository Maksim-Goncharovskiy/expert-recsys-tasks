from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    rate = State() # состояние оценки фильмов