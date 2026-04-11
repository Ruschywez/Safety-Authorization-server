from peewee import SqliteDatabase
from pathlib import Path
from logger_config import setup_logger

def take_db_connect() -> SqliteDatabase:
    _logger = setup_logger(__name__)  # logger creating
    _logger.debug("Trying to connect...")
    _db_path = Path(__file__).resolve().parent.parent / 'database.db'
    db = SqliteDatabase(_db_path, pragmas={'foreign_keys': 1})
    db.connect() # DB is already will have active connect
    return db
