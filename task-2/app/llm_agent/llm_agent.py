import os
import json
from dataclasses import dataclass, field 
from openai import AsyncOpenAI
from .database_manager import DatabaseManager, DatabaseResults
from .exceptions import DatabaseSchemaFileNotExists, ClassificationError, SqlQueryGenerationError, GeneralAnswerGenerationError, FinalAnswerGenerationError


@dataclass 
class LLMAgentConfig:
    api_key: str
    url: str
    db_path: str
    db_schema_path: str
    model: str


class LLMAgent:
    def __init__(self, config: LLMAgentConfig):
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.url
        )

        self.db_manager = DatabaseManager(db_path=config.db_path)

        if not os.path.exists(config.db_schema_path):
            raise DatabaseSchemaFileNotExists(f"Описание базы данных по пути {config.db_schema_path} не найдено!")        
        
        with open(config.db_schema_path, 'r', encoding='utf-8') as txt:
            self.prompt_db = ' '.join(txt.readlines())
        
        self.model = config.model
    

    async def classify_query(self, user_query: str):
        """Классифицирует запрос: нужна ли база данных"""
        
        prompt = f"""
Ты онлайн ассистент для работников библиотеки. Твоя задача — определить, нужен ли запрос к базе данных для получения сведений об имеющихся в базе данных авторах, книгах, читателях.

Ответь ТОЛЬКО одной цифрой:
1 - если нужен (вопросы о наличии книг, авторах, читателях и т.п.)
0 - во всех остальных случаях (общие вопросы, приветствия и т.п.)

Примеры:
"Книги скольких авторов есть в библиотеке?" -> 1
"Привет, расскажи о библиотеке" -> 0 
"Какого жанра книг в библиотеке больеш всего?" -> 1
"Что ты думаешь о Достоевском?" -> 0

Запрос: {user_query}

Ответ:

"""
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0,
                max_tokens=5
            )
            
            result = response.choices[0].message.content.strip()
            classification = 1 if result == '1' else 0

            return classification
            
        except Exception as err:
            error_msg = f"Ошибка классификации: {err}"
            raise ClassificationError(error_msg)
    

    async def generate_sql_query(self, user_query):
        """Генерирует SQL-запрос для получения данных"""
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql_query",
                    "description": "Выполняет SQL-запрос к базе данных библиотеки",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                                "description": "SQL-запрос SELECT для выполнения"
                            }
                        },
                        "required": ["sql_query"]
                    }
                }
            }
        ]
        
        prompt = f"""
    Ты опытный аналитик данных. На основе схемы базы данных и вопроса пользователя, 
    сгенерируй корректный SQL-запрос SELECT для получения нужной информации.

    СХЕМА БАЗЫ ДАННЫХ:
    {self.prompt_db}

    ВОПРОС ПОЛЬЗОВАТЕЛЯ:
    {user_query}

    ИНСТРУКЦИИ:
    1. Создай ТОЛЬКО один SQL-запрос SELECT
    2. Используй только таблицы и колонки, указанные в схеме
    3. ВЫЗОВИ функцию execute_sql_query с готовым SQL-запросом

    """
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                model=self.model,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "execute_sql_query"}}
            )
            
            # Извлекаем вызов инструмента
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                if tool_call.function.name == "execute_sql_query":
                    function_args = json.loads(tool_call.function.arguments)
                    sql_query = function_args.get("sql_query", "")
                    return sql_query
                
                else:
                    error_msg = f"Ошибка при генерации SQL-запроса агентом. Агент вызвал не ту функцию. Вызванная функция: {tool_call.function.name}. Нужно было вызвать: execute_sql_query."
                    raise SqlQueryGenerationError(error_msg)
                
            else:
                error_msg = f"Ошибка при генерации SQL-запроса агентом. Агент не вызвал ни одного инструмента. Нужно было вызвать функцию execute_sql_query."
                raise SqlQueryGenerationError(error_msg)
        

        except SqlQueryGenerationError as err:
            raise SqlQueryGenerationError(err)
        

        except Exception as err:
            error_msg = f"Ошибка при генерации SQL-запроса: {err}"
            raise SqlQueryGenerationError(error_msg)
    

    async def generate_general_query(self, user_query: str) -> str:
        """Получает общий ответ от LLM (не связанный с базой)"""

        prompt = f"""
Ты полезный и вежливый ассистент, отвечающий за предоставление информации о библиотеке. Ты должен сказать, что умеешь искать информацию о книгах, авторах и читателях библиотеки. Коротко ответь на вопрос пользователя.

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{user_query}

Ответь дружелюбно и по существу. Строго запрещено давать пустой ответ, обязательно напиши что-нибудь.

ТВОЙ ОТВЕТ:
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0,
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip()
            
            return result
            
        except Exception as err:
            error_msg = f"Ошибка генерации общего ответа: {err}"
            raise GeneralAnswerGenerationError(error_msg)
    

    async def generate_final_answer(self, user_query: str, db_results: DatabaseResults) -> str:
        results = db_results.results

        prompt = f"""
Ты ассистент, отвечающий за предоставление информации о библиотеке. На основе вопроса пользователя и полученных данных из базы, 
сформируй понятный и полезный ответ.

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{user_query}

РЕЗУЛЬТАТЫ ЗАПРОСА К БАЗЕ:
{json.dumps(results, ensure_ascii=False, indent=2)}

ИНСТРУКЦИИ:
1. Ответь на вопрос пользователя, используя данные из базы
2. Сформулируй ответ понятным, дружелюбным языком
3. Если данных нет, честно об этом скажи
4. Строго запрещено давать пустой ответ, обязательно напиши что-нибудь.

ТВОЙ ОТВЕТ:
"""
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            return result
            
        except Exception as err:
            error_msg = f"Ошибка генерации финального ответа: {err}"
            raise FinalAnswerGenerationError(error_msg)
    

    async def __call__(self, user_query: str) -> str:
        clf: int = await self.classify_query(user_query)
        answer: str = ''

        if clf == 0:
            answer = await self.generate_general_query(user_query)
        else:
            sql_query: str = await self.generate_sql_query(user_query)

            db_result: DatabaseResults = self.db_manager.execute_query(sql_query)

            answer = await self.generate_final_answer(user_query, db_result)
        
        return answer


        

        