from .csv_db_manager import CsvDatabaseConfig, CsvMovieDatabaseManager
from config import CONFIG



db_manager = CsvMovieDatabaseManager(config=CsvDatabaseConfig(
    db_path=CONFIG.db.path,
    user_table=CONFIG.db.user_table,
    movie_table=CONFIG.db.movie_table))