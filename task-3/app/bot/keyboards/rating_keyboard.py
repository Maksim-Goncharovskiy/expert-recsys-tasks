from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# кнопки выбора оценки
rates_buttons = [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]

# кнопка выбора модели gpt-oss-120b
finish_button = InlineKeyboardButton(
    text="Закончить оценивание",
    callback_data="finish_rating"
)


rating_keyboard = InlineKeyboardMarkup(inline_keyboard=[rates_buttons, [finish_button]])