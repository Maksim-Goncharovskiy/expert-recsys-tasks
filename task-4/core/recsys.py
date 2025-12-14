from abc import ABCMeta, abstractmethod


class RecSys(metaclass=ABCMeta):
    @abstractmethod
    def provide_recommendation(self, user_id: int, n_movies: int = 5, **kwargs) -> set[str]:
        """
        Предлагает список рекомендуемых фильмов для пользователя.
        Параметры:
            * n_movies: int - количество рекомендуемых фильмов
        Возвращает:
            set[str] - множество названий рекомендованных фильмов
        """
        pass 