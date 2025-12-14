import logging
import math
import numpy as np
import pandas as pd
from core import RecSys, MovieDatabaseManager


logger = logging.getLogger(__name__)


class UserNotFound(ValueError):
    pass 


class ColdStartError(ValueError):
    pass


class SVDppRecSys(RecSys):
    def __init__(
        self, 
        db_manager: MovieDatabaseManager, 
        n_factors: int = 20, 
        n_epochs: int = 25, 
        lr: float = 0.05, 
        lr_alpha: float = 0.95,
        reg: float = 0.02, 
        cold_start_threshold: int = 3
    ):
        """
        Инициализация SVD++ рекомендательной системы
        
        :param db_manager: объект для работы с базой данных фильмов и оценок
        :param n_factors: размерность латентных векторов
        :param n_epochs: количество эпох обучения
        :param lr: скорость обучения
        :param reg: коэффициент регуляризации
        :param cold_start_threshold: порог в количестве оценённых фильмов для получения рекомендации
        """
        self.db_manager = db_manager
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.lr_alpha = lr_alpha
        self.reg = reg
        self.cold_start_threshold = cold_start_threshold
        
        ratings_df: pd.DataFrame = self.db_manager.get_user_movie_data()
        
        self.num_users, self.num_items = ratings_df.shape
        
        scale = 0.1 / math.sqrt(self.n_factors)
        
        # Инициализируем обучаемые параметры системы
        self.user_factors = np.random.normal(
            scale=scale, 
            size=(self.num_users, self.n_factors)
        )

        self.item_factors = np.random.normal(
            scale=scale, 
            size=(self.num_items, self.n_factors)
        )
        
        self.user_biases = np.zeros(self.num_users)
        self.item_biases = np.zeros(self.num_items)

        # средняя оценка по всему датасету
        self.global_mean = np.nanmean(ratings_df.values)
        
        # маппим айдишники и индексы 
        self.user_ids = list(ratings_df.index)
        self.item_ids = list(ratings_df.columns)
        
        self.user_id_to_idx = {uid: idx for idx, uid in enumerate(self.user_ids)}
        self.item_id_to_idx = {iid: idx for idx, iid in enumerate(self.item_ids)}
        
        self.user_idx_to_id = {idx: uid for idx, uid in enumerate(self.user_ids)}
        self.item_idx_to_id = {idx: iid for idx, iid in enumerate(self.item_ids)}

        self.user_items = {}  # user_idx -> list[item_idx]

        train_data = []  # (user_idx, item_idx, rate)
        
        for user_idx, user_id in enumerate(self.user_ids):
            user_ratings = ratings_df.loc[user_id]
            rated_items = user_ratings.dropna()
            
            self.user_items[user_idx] = []
            
            for item_id, rating in rated_items.items():
                item_idx = self.item_id_to_idx[item_id]
                train_data.append((user_idx, item_idx, rating))
                self.user_items[user_idx].append(item_idx)

        self.train(train_data=train_data)

    
    def _calc_user_implicit_vector(self, user_idx: int) -> np.ndarray:
        """
        Вычисление вектора неявных предпочтений для пользователя
        
        :param user_idx: индекс пользователя
        :return: вектор скрытых предпочтений (размерности self.n_factors)
        """
        if user_idx not in self.user_items or not self.user_items[user_idx]:
            return np.zeros(self.n_factors)
        
        items = self.user_items[user_idx]
        implied_sum = np.sum(self.item_factors[items], axis=0)

        return implied_sum / len(items)
    

    def predict_user_rate(self, user_id: int, item_id: int) -> float:
        """
        Предсказание оценки пользователя для фильма
        
        :param user_id: ID пользователя
        :param item_id: ID фильма
        :return: предсказанная оценка (вещественное число от 1 до 5)
        """
        if user_id not in self.user_id_to_idx or item_id not in self.item_id_to_idx:
            return self.global_mean
        
        user_idx = self.user_id_to_idx[user_id]
        item_idx = self.item_id_to_idx[item_id]
        
        user_vector = self.user_factors[user_idx] + self._calc_user_implicit_vector(user_idx)
        item_vector = self.item_factors[item_idx]

        rate = self.global_mean + self.user_biases[user_idx] + self.item_biases[item_idx] + np.dot(user_vector, item_vector)        
        
        return np.clip(rate, 1.0, 5.0)
    

    def train(self, 
              train_data: list[tuple[int, int, int]], 
              n_epochs: int | None = None, 
              lr: float | None = None, 
              lr_alpha: float | None = None,
              reg: float | None = None) -> None:
        """
        Обучение параметров рекомендательной системы
        
        :param train_data: Обучающие данные в формате (user_idx, item_idx, rate)
        :type train_data: list[tuple[int, int, int]]
        :param n_epochs: Количество эпох обучения (по умолчанию используется self.n_epochs)
        :type n_epochs: int | None
        :param lr: Параметр для регулирования шага оптимизации (скорость обучения)
        :type lr: float | None
        :param lr_alpha: Коэффициент изменения lr после каждой эпохи.
        :type lr_aplha: float | None
        """
        n_epochs = n_epochs if n_epochs else self.n_epochs
        lr = lr if lr else self.lr 
        lr_alpha = lr_alpha if lr_alpha else self.lr_alpha
        reg = reg if reg else self.reg

        logger.info(f"Начало обучения рекомендательной системы на базе SVD++")
        logger.info(f"Количество эпох: {n_epochs}")
        
        for epoch in range(n_epochs):
            total_loss = 0
            num_samples = 0
            
            for user_idx, item_idx, true_rating in train_data:
                implied_vector = self._calc_user_implicit_vector(user_idx)
                
                rate_pred = (
                    self.global_mean +
                    self.user_biases[user_idx] +
                    self.item_biases[item_idx] +
                    np.dot(self.user_factors[user_idx] + implied_vector, 
                          self.item_factors[item_idx])
                )
                
                error = true_rating - rate_pred
                total_loss += error ** 2
                
                user_grad = (
                    error * self.item_factors[item_idx] -
                    reg * self.user_factors[user_idx]
                )
                
                item_grad = (
                    error * (self.user_factors[user_idx] + implied_vector) -
                    reg * self.item_factors[item_idx]
                )
                
                user_bias_grad = error - reg * self.user_biases[user_idx]
                item_bias_grad = error - reg * self.item_biases[item_idx]
                
                self.user_factors[user_idx] += lr * user_grad
                self.item_factors[item_idx] += lr * item_grad
                self.user_biases[user_idx] += lr * user_bias_grad
                self.item_biases[item_idx] += lr * item_bias_grad
                
                num_samples += 1
            
            lr *= lr_alpha
            
            avg_loss = total_loss / num_samples if num_samples > 0 else 0
            print(f"  Эпоха {epoch + 1}/{n_epochs}, Loss: {avg_loss:.4f}")
    

    def finetune_user(self, user_id: int, n_epochs: int | None = None, lr: float | None = None, ) -> None:
        # 1. Проверяем новый это пользователь или старый
        if user_id not in self.user_id_to_idx:
            self.user_ids.append(user_id)
                
            scale = 0.1 / math.sqrt(self.n_factors)
                
            new_user_factor = np.random.normal(
                scale=scale, 
                size=(1, self.n_factors)
            )
            self.user_factors = np.vstack([self.user_factors, new_user_factor])
                
            self.user_biases = np.append(self.user_biases, 0.0)
                
            new_user_idx = len(self.user_ids) - 1
            self.user_id_to_idx[user_id] = new_user_idx
            self.user_idx_to_id[new_user_idx] = user_id
                
            self.user_items[new_user_idx] = []
                
            self.num_users += 1

        # 2. Читаем таблицу с оценками и актуализируем информацию о пользователе
        ratings_df: pd.DataFrame = self.db_manager.get_user_movie_data()
        user_idx = self.user_id_to_idx[user_id]
        
        self.user_items[user_idx] = []
        
        train_data = []
        if user_id in ratings_df.index:
            user_ratings = ratings_df.loc[user_id]
            rated_items = user_ratings.dropna()
            
            train_data = []
            
            for item_id, rating in rated_items.items():
                if item_id in self.item_id_to_idx:
                    item_idx = self.item_id_to_idx[item_id]
                    train_data.append((user_idx, item_idx, rating))
                    self.user_items[user_idx].append(item_idx)

        # 3. Формируем обучающие данные и запускаем дообучение
        if train_data:
            self.train(train_data=train_data)
        else: 
            logger.warning("У пользователя нет оценок, обучение пропущено!")
        
 


    def provide_recommendation(self, user_id: int, n_movies: int = 5) -> set[str]:
        """
        Формирование рекомендаций для пользователя
        
        :param user_id: ID пользователя
        :param n_movies: количество фильмов для рекомендации
        :return: множество названий рекомендованных фильмов
        """
        # 1. Проверяем есть ли пользователь в базе и оценил ли он достаточное количество фильмов
        if user_id not in self.user_id_to_idx:
            msg = f"Пользователь {user_id} не найден в системе"
            logger.warning(msg)
            raise UserNotFound(msg)
        
        user_idx = self.user_id_to_idx[user_id]

        if user_idx not in self.user_items or len(self.user_items[user_idx]) < self.cold_start_threshold:
            msg = f"У пользователя {user_id} недостаточно оценок. Минимальное количество: {self.cold_start_threshold}"
            logger.warning(msg)
            raise ColdStartError(msg)

        # 2. Предсказываем его оценки для всех фильмов, которые он еще не оценил
        user_new_movies: list[str] = list(self.db_manager.get_user_new_movies(user_id))
        user_new_movies: list[int] = [self.db_manager.movie_title_to_id(movie) for movie in user_new_movies]

        predictions = []
        for movie_id in user_new_movies:
            rate_pred = self.predict_user_rate(user_id=user_id, item_id=movie_id)
            predictions.append((movie_id, rate_pred))

        # 3. Сортируем полученные оценки по убыванию и возвращаем названия соответствующих им фильмов
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_n = predictions[:n_movies]
        
        recommendation: set[str] = set()
        for rec in top_n:
            movie_title: str = self.db_manager.movie_id_to_title(rec[0])
            recommendation.add(movie_title)
        
        return recommendation

