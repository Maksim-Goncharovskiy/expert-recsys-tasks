from abc import ABCMeta, abstractmethod


class UserBasedCollaborativeFiltering(metaclass=ABCMeta):
    @abstractmethod
    def provide_recommendation(self, user_id: int, n_movies: int = 5, n_neighbors: int = 5) -> set[str]:
        """
        Предлагает список рекомендуемых фильмов для пользователя.
        Параметры:
            * n_movies: int - количество рекомендуемых фильмов
            * n_neighbors: int - количество рассматриваемых наиболее близких пользователей, из которых будут 
                формироваться рекомендации
        """
        pass 