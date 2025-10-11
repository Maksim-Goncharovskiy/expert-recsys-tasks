"""Исключения при работе с базой данных"""

class DatabaseError(ValueError):
    pass


class DatabaseFileNotExists(DatabaseError):
    pass 


class NotSelectQuerySuggested(DatabaseError):
    pass 


class SqlQueryExecutionError(DatabaseError):
    pass


"""Исключения при работе с агентами"""

class AgentError(Exception):
    pass 


class DatabaseSchemaFileNotExists(AgentError):
    pass


class ClassificationError(AgentError):
    pass


class SqlAgentError(AgentError):
    pass 


class SqlQueryGenerationError(AgentError):
    pass 


class GeneralAnswerGenerationError(AgentError):
    pass


class FinalAnswerGenerationError(AgentError):
    pass