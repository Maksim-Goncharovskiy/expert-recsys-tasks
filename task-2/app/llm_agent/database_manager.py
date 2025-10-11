import os
import sqlite3
import logging
from dataclasses import dataclass, field
from .exceptions import DatabaseFileNotExists, NotSelectQuerySuggested, SqlQueryExecutionError



@dataclass
class DatabaseResults:
    """Формат возвращаемых результатов после выполнения запроса к базе данных"""
    executed_sql_query: str = field(repr=True)
    results: list[dict] = field(repr=True, default_factory=list)
    count: int = field(repr=True, default=0) 



class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

        if not os.path.exists(self.db_path):
            raise DatabaseFileNotExists(f"Файл базы данных по пути: {self.db_path} не найден!")
    

    def execute_query(self, sql_query) -> DatabaseResults:
        """Выполняет SQL-запрос и возвращает результаты"""
        try:
            # Безопасность: разрешаем только SELECT запросы
            clean_query = sql_query.strip().upper()
            if not clean_query.startswith("SELECT"):
                error_msg = f"Допустимы только SELECT запросы. Был предожен следующий запрос: {clean_query}"
                raise NotSelectQuerySuggested(error_msg)

            # Проверяем существование файла базы
            if not os.path.exists(self.db_path):
                error_msg = f"Файл базы данных по пути: {self.db_path} не найден!"
                raise DatabaseFileNotExists(error_msg)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Для получения словарей
            cursor = conn.cursor()
            
            # Выполняем запрос
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Преобразуем в список словарей
            results = [dict(row) for row in rows]
            
            conn.close()

            return DatabaseResults(
                results=results,
                count=len(results),
                executed_sql_query=sql_query
            )
        
        except NotSelectQuerySuggested as err:
            raise NotSelectQuerySuggested(err)
        

        except DatabaseFileNotExists as err:
            raise DatabaseFileNotExists(err)
        

        except sqlite3.Error as err:
            error_msg = f"Ошибка обращения к базе данных: {str(err)}"
            raise SqlQueryExecutionError(error_msg)
        

        except Exception as err:
            error_msg = f"Неизвестная ошибка при обращении к базе данных: {str(err)}"
            raise SqlQueryExecutionError(error_msg)