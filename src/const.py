from pathlib import Path as _Path
from src.entities import Usr as _Usr, Session as _Session, Secret as _Secret

DB_PATH = _Path(__file__).resolve().parent.parent / 'database.db'
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"
DB_TABLES = (_Usr, _Session, _Secret)

LOG_PATH = _Path(__file__).resolve().parent.parent / 'logs'

ENV_PATH = _Path(__file__).resolve().parent.parent / '.env'

EXPIRATION_TIME = 30 # days

EMAIL_RE_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'