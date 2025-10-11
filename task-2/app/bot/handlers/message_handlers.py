from redis.asyncio import Redis
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from app.bot.lexicon import LEXICON_RU
from app.llm_agent import LLMAgent, LLMAgentConfig, DatabaseError, AgentError
from config import Config, load_config


CONFIG: Config = load_config()

REDIS = Redis(host=CONFIG.redis.host, port=CONFIG.redis.port)


message_router = Router()


@message_router.message(F.text)
async def process_user_query(message: Message):
    model = await REDIS.get(f"{message.from_user.id}")
    model = model.decode()

    if not model:
        model = 'qwen3-coder'

    try:
        llm_config: LLMAgentConfig = LLMAgentConfig(
            api_key=CONFIG.llm_api.api_key,
            url=CONFIG.llm_api.url,
            db_path=CONFIG.db.path,
            db_schema_path=CONFIG.db.schema_path,
            model=model
        )

        llm_agent = LLMAgent(llm_config)

        answer = await llm_agent(message.text)

        if answer:
            await message.answer(answer)
        else:
            await message.answer(LEXICON_RU["empty_answer"])

    except DatabaseError as err:
        await message.answer(LEXICON_RU["db_error"])
    
    except AgentError as err:
        await message.answer(LEXICON_RU["agent_error"] + f" {err}")

    except Exception as err:
        await message.answer(LEXICON_RU["unknown_error"])