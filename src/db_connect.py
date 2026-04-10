from peewee import SqliteDatabase
from pathlib import Path
from logger_config import setup_logger

_logger = setup_logger(__name__)  # logger creating
_logger.debug("Trying to connect...")
_db_path = Path(__file__).resolve().parent.parent / 'database.db'
db = SqliteDatabase(_db_path, pragmas={'foreign_keys': 1})
db.connect()
_logger.debug("Loading entities...")
from entities import User, user_db, Secret, secret_db, Session, session_db

user_db.initialize(db)
secret_db.initialize(db)
session_db.initialize(db)

