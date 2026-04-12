import os
from pathlib import Path
from src.logger_config import setup_logger
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
import bcrypt

class CryptManager:
    def __init__(self):
        self.__logger = setup_logger(__name__)  # logger creating
        self.__fernet = None
        self.__logger.debug("Checking env for keys...")

        # download .env before reading data
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(env_path)

        try:  # try to load keys
            self.__key = self.__load_key()
            self.__logger.info("Keys successfully downloaded")
        except ValueError as e:  # if error then create it
            self.__logger.warning(e)
            self.__key = self.__create_key(env_path)
            self.__logger.info("Keys were created successfully")

        self.__fernet = Fernet(self.__key)

    def __load_key(self) -> bytes:
        ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
        if ENCRYPTION_KEY is None:
            raise ValueError("ENCRYPTION_KEY is not found")
        ENCRYPTION_KEY = bytes.fromhex(ENCRYPTION_KEY)
        return ENCRYPTION_KEY

    def __create_key(self, env_path: Path) -> bytes:
        ENCRYPTION_KEY = Fernet.generate_key()
        # save to env with absolute path
        # because env not inside env -_-
        set_key(str(env_path), 'ENCRYPTION_KEY', ENCRYPTION_KEY.hex())
        return ENCRYPTION_KEY

    """encrypt&decrypt data methods"""
    async def encrypt(self, text: str) -> str:
        if not text:
            raise ValueError("Text cannot be empty or None!")
        # str -> bytes -> encrypt -> bytes -> str
        return self.__fernet.encrypt(text.encode()).decode()

    async def decrypt(self, text: str) -> str:
        # str -> bytes -> decrypt -> bytes -> str
        return self.__fernet.decrypt(text.encode()).decode()
    
    async def encrypt_bytes(self, data: bytes) -> bytes:
        if not data:
            raise ValueError("Data cannot be empty or None!")
        # bytes -> encrypt -> bytes
        return self.__fernet.encrypt(data)

    async def decrypt(self, data: bytes) -> bytes:
        # bytes -> decrypt -> bytes
        return self.__fernet.decrypt(data)

    """password's methods"""
    async def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    async def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
