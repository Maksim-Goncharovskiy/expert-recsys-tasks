import logging
from redis.asyncio import Redis
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from app.bot.lexicon import LEXICON_RU
from app.llm_agent import LLMAgent, LLMAgentConfig, DatabaseError, AgentError
from config import Config, load_config



logger = logging.getLogger(__name__)


CONFIG: Config = load_config()

REDIS = Redis(host=CONFIG.redis.host, port=CONFIG.redis.port)


message_router = Router()


@message_router.message(F.text)
async def process_user_query(message: Message):
    """Обработка обычного текстового сообщения от пользователя"""
    await message.bot.send_chat_action(message.chat.id, "typing")

    logger.info(f"Получено сообщение от пользователя {message.from_user.id}: {message.text}.")
    logger.info(f"Попытка получить выбранную пользователем модель из redis")
    model = await REDIS.get(f"{message.from_user.id}")
    model = model.decode()

    if not model:
        model = 'qwen3-coder'
        logger.info(f"Пользователь не выбрал модель. По умолчанию используется: {model}")

    try:
        logger.info(f"Начало обработки запроса LLM-агентом. Выполняется конфигурация LLM-агента.")

        await message.bot.send_chat_action(message.chat.id, "typing")

        llm_config: LLMAgentConfig = LLMAgentConfig(
            api_key=CONFIG.llm_api.api_key,
            url=CONFIG.llm_api.url,
            db_path=CONFIG.db.path,
            db_schema_path=CONFIG.db.schema_path,
            model=model
        )

        llm_agent = LLMAgent(llm_config)

        logger.info(f"LLM-агент запущен.")

        answer = await llm_agent(message.text)

        await message.bot.send_chat_action(message.chat.id, "typing")

        logger.info(f"Получен ответ от LLM-агента: {answer}")

        if answer:
            await message.answer(answer)
        else:
            await message.answer(LEXICON_RU["empty_answer"])

    except DatabaseError as err:
        logger.error(f"Была получена ошибка при работе с базой данных: {err}")
        await message.answer(LEXICON_RU["db_error"])
    
    except AgentError as err:
        logger.error(f"Была получена ошибка при работе агента: {err}")
        await message.answer(LEXICON_RU["agent_error"] + f" {err}")

    except Exception as err:
        logger.error(f"Была получена неизвестная ошибка: {err}")
        await message.answer(LEXICON_RU["unknown_error"])