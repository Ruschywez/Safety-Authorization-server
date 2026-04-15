from pathlib import Path
from src.entities import Usr, Session, Secret

CORE_PATH = Path(__file__).resolve().parent.parent

DB_PATH = CORE_PATH / 'database.db'
LOG_PATH = CORE_PATH / 'logs'
ENV_PATH = CORE_PATH / '.env'

AVATAR_PATH = CORE_PATH / 'resources' / 'avatars'
SECRET_PATH = CORE_PATH / 'resources' / 'secrets'

DB_URL = f"sqlite:///{DB_PATH.as_posix()}"
DB_TABLES = (Usr, Session, Secret)



EXPIRATION_TIME = 30 # days

EMAIL_RE_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'