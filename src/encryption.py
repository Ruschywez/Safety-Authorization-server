import os
from pathlib import Path
from src.logger_config import setup_logger
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
import bcrypt

class CryptManager:
    def __init__(self):
        self.logger = setup_logger(__name__)  # logger creating
        self.__fernet = None
        self.logger.debug("Checking env for keys...")

        # Загружаем .env перед чтением переменных
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(env_path)

        try:  # try to load keys
            self.__key = self.__load_key()
            self.logger.info("Keys successfully downloaded")
        except ValueError:  # if error then create it
            self.logger.warning("EnvironmentError")
            self.__key = self.__create_key(env_path)
            self.logger.info("Keys were created successfully")

        self.__fernet = Fernet(self.__key)

    def __load_key(self) -> bytes:
        ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
        if ENCRYPTION_KEY is None:
            raise ValueError
        ENCRYPTION_KEY = bytes.fromhex(ENCRYPTION_KEY)
        return ENCRYPTION_KEY

    def __create_key(self, env_path: Path) -> bytes:
        ENCRYPTION_KEY = Fernet.generate_key()
        # save to env with absolute path
        set_key(str(env_path), 'ENCRYPTION_KEY', ENCRYPTION_KEY.hex())
        return ENCRYPTION_KEY

    """encrypt&decrypt data"""
    def encrypt(self, text: str) -> str:
        # str -> bytes -> encrypt -> bytes -> str
        return self.__fernet.encrypt(text.encode()).decode()

    def decrypt(self, text: str) -> str:
        # str -> bytes -> decrypt -> bytes -> str
        return self.__fernet.decrypt(text.encode()).decode()

    """password"""
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
