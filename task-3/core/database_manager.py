from abc import ABCMeta, abstractmethod


class DatabaseError(ValueError):
    pass 

class DatabaseNotExists(DatabaseError):
    pass 

class UserTableNotExists(DatabaseError):
    pass 

class MovieTableNotExists(DatabaseError):
    pass 



class MovieDatabaseManager(metaclass=ABCMeta):
    @abstractmethod
    def movie_title_to_id(self, movie_title: str) -> int:
        """Получить id фильма по его названию"""
        pass


    @abstractmethod
    def movie_id_to_title(self, movie_id: int) -> str:
        """Получить название фильма по его id"""
        pass


    @abstractmethod
    def get_user_new_movies(self, user_id: int) -> set[str]:
        """Получить для пользователя список еще не оценённых фильмов"""
        pass 
    

    @abstractmethod
    def set_user_movie_rate(self, user_id: int, movie_title: str) -> bool:
        """
        Обновить пользовательскую оценку фильма в БД.
        Возвращает bool:
            - True, если операция прошла успешно
            - False, если возникла ошибка записи в БД.
        """
        pass 


    @abstractmethod
    def get_user_movie_data(self):
        """
        Получение таблицы в формате user_x_movies (строка - это пользователи, столбцы - id фильмов, значения - оценки от 1 до 5)
        """
        pass 