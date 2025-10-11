from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.bot.lexicon import LEXICON_RU


# кнопка выбора модели qwen3-coder
qwen_button = InlineKeyboardButton(
    text=LEXICON_RU["buttons"]["qwen3-coder"],
    callback_data="qwen3-coder"
)

# кнопка выбора модели gpt-oss-120b
gpt_button = InlineKeyboardButton(
    text=LEXICON_RU["buttons"]["gpt-oss-120b"],
    callback_data="gpt-oss-120b"
)


model_keyboard = InlineKeyboardMarkup(inline_keyboard=[[qwen_button], [gpt_button]])