import asyncio
from app.llm_agent.llm_agent import LLMAgent, LLMAgentConfig
from config import Config, load_config


async def main():
    config: Config = load_config()

    llm_config = LLMAgentConfig(api_key=config.llm_api.api_key,
                   url=config.llm_api.url,
                   db_path=config.db.path,
                   db_schema_path='./db_schema.txt',
                   model='qwen3-coder')
    agent = LLMAgent(llm_config)

    answer = await agent("Какие книги достоевского есть в библиотеке?")

    print(answer)


if __name__ == "__main__":
    asyncio.run(main=main())


