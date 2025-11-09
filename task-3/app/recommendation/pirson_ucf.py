import math
import numpy as np
import pandas as pd
from core import UserBasedCollaborativeFiltering, MovieDatabaseManager


class PirsonUCF(UserBasedCollaborativeFiltering):
    def __init__(self, db_manager: MovieDatabaseManager):
        self.db_manager = db_manager


    def pirson_similarity(self, user_1: np.ndarray, user_2: np.ndarray):
        """Расчёт похожести двух пользователей по коэффициенту Пирсона"""

        common_movies = (~np.isnan(user_1)) & (~np.isnan(user_2))

        if not np.any(common_movies):
            return 0.0
        
        user_1_common = user_1[common_movies]
        user_2_common = user_2[common_movies]

        if len(user_1_common) < 2:
            return 0.0
        
        mean_user_1 = np.mean(user_1_common)
        mean_user_2 = np.mean(user_2_common)

        # вычисление числителя
        numerator = 0.0
        for i in range(len(user_1_common)):
            numerator += (user_1_common.iloc[i] - mean_user_1) * (user_2_common.iloc[i] - mean_user_2)

        # вычисление знаменателя
        sum_sq_user_1 = 0.0
        sum_sq_user_2 = 0.0
        
        for i in range(len(user_1_common)):
            sum_sq_user_1 += (user_1_common.iloc[i] - mean_user_1) ** 2
            sum_sq_user_2 += (user_2_common.iloc[i] - mean_user_2) ** 2
        
        denominator = math.sqrt(sum_sq_user_1) * math.sqrt(sum_sq_user_2 )

        if denominator == 0:
            return 0.0
        
        return numerator / denominator


    def provide_recommendation(self, user_id, n_movies = 5, n_neighbors: int = 5):
        ratings: pd.DataFrame = self.db_manager.get_user_movie_data()

        # Если пользователя нет, возвращаем случайные фильмы
        if user_id not in ratings.index:
            all_movie_ids = ratings.columns.tolist()
            random_movies = np.random.choice(all_movie_ids, size=min(n_movies, len(all_movie_ids)), replace=False)
            return [self.db_manager.movie_id_to_title(movie_id) for movie_id in random_movies]

        target_user_ratings = ratings.loc[user_id]

        # Вычисляем схожесть со всеми другими пользователями
        similarities = []
        for other_user_id in ratings.index:
            if other_user_id == user_id:
                continue
                
            other_user_ratings = ratings.loc[other_user_id]
            similarity = self.pirson_similarity(target_user_ratings, other_user_ratings)
            similarities.append((other_user_id, similarity))

        # Сортируем по убыванию схожести и берем n_neighbors ближайших соседей
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_neighbors = similarities[:n_neighbors]

        target_user_new_movies = self.db_manager.get_user_new_movies(user_id=user_id)

        recommendation = set()
        
        for neighbor_id, similarity in top_neighbors:
            neighbor_ratings = ratings.loc[neighbor_id]
            
            neighbor_good_movies = neighbor_ratings[neighbor_ratings >= 4].index
            
            if len(recommendation) >= n_movies:
                break 

            for movie_id in neighbor_good_movies:
                movie_title = self.db_manager.movie_id_to_title(movie_id=movie_id)
                if movie_title in target_user_new_movies:
                    recommendation.add(movie_title)
                    if len(recommendation) >= n_movies:
                        break
        
        # если вдруг не получилось извлечь достаточно рекомендаций добавляем случайных
        if len(recommendation) < n_movies:
            additional_movies_cnt = n_movies - len(recommendation)
            additional_movies = np.random.choice(target_user_new_movies, size=additional_movies_cnt, replace=False)
            recommendation.update(additional_movies)
            
        return recommendation