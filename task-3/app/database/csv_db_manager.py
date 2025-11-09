import os 
from dataclasses import dataclass, field
import pandas as pd
import csv

from core import MovieDatabaseManager, DatabaseNotExists, UserTableNotExists, MovieTableNotExists


@dataclass
class CsvDatabaseConfig:
    db_path: str = field(repr=True)
    user_table: str = field(repr=True)
    movie_table: str = field(repr=True)


class CsvMovieDatabaseManager(MovieDatabaseManager):
    def __init__(self, config: CsvDatabaseConfig):
        self.config = config

        if not os.path.exists(self.config.db_path):
            raise DatabaseNotExists
        
        if not os.path.exists(self.config.db_path + self.config.user_table):
            raise UserTableNotExists

        if not os.path.exists(self.config.db_path + self.config.movie_table):
            raise MovieTableNotExists
        
        self.id2title = dict()
        self.title2id = dict()

        self.id2title: dict[int, str] = pd.read_csv(self.config.db_path+self.config.movie_table,
                    names=('movie','title'),
                    header=None, 
                    encoding='latin-1', 
                    sep='|', 
                    usecols=(0,1), index_col=0).to_dict()['title']
        
        self.title2id: dict[str, int] = {value: key for key, value in self.id2title.items()}
    

    def movie_id_to_title(self, movie_id):
        return self.id2title.get(movie_id, None)
    
    
    def movie_title_to_id(self, movie_title):
        return self.title2id.get(movie_title, None)
    

    def get_user_movie_data(self) -> pd.DataFrame:
        ratings = pd.read_csv(
            self.config.db_path + self.config.user_table, 
            sep='\t', header=None, names=["user_id", "movie_id", "rate", "timestamp"])
        
        return ratings.pivot_table(
            index='user_id',      
            columns='movie_id',   
            values='rate',        
            fill_value=None)
    

    def get_user_new_movies(self, user_id: int):
        ratings_df: pd.DataFrame = self.get_user_movie_data()
        
        user_new_movies: set = set()

        if user_id in ratings_df.index:
            user_ratings: pd.Series = ratings_df.loc[user_id]

            user_new_movies_id = user_ratings[user_ratings.isna()].index

            for movie_id in user_new_movies_id:
                movie_title: str = self.id2title.get(movie_id, None)
                if movie_title:
                    user_new_movies.add(movie_title)
        else:
            user_new_movies.update(list(self.title2id.keys()))
            
        return user_new_movies


    def set_user_movie_rate(self, user_id: int, movie_title: str, rate: int) -> bool:
        try:
            movie_id = self.title2id.get(movie_title, None)

            if movie_id:
                with open(self.config.db_path + self.config.user_table, mode='a', newline='') as file:
                    writer = csv.writer(file, delimiter='\t')
                    writer.writerow([user_id, movie_id, rate, None])
                return True
            
            else:
                return False
            
        except Exception as err:
            print(err)
            return False