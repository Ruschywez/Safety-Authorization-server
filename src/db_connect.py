from peewee import SqliteDatabase
from logging import Logger
from pathlib import Path
from peewee import Proxy
from peewee_aio import Manager
from src.logger_config import setup_logger

class DataBase:
    def __init__(self, *tables):
        self.tables: tuple = tables
        self.__logger: Logger = setup_logger(__name__)
        self.__logger.debug("Trying to connect...")
        self.manager = Manager(self.__get_database_url())

    async def init(self):
        self.__logger.debug("Creating tables...")
        for table in self.tables:
            self.manager.register(table)
        await self.manager.create_tables(*self.tables)
        self.__logger.info("Database is ready to work!")

    def __get_database_url(self) -> str:
        db_path = Path(__file__).resolve().parent / 'database.db'
        return f"sqlite:///{db_path.as_posix()}"
