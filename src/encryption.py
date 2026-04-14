import os as _os
from pathlib import Path as _Path
from dotenv import load_dotenv as _load_dotenv, set_key as _set_key
from cryptography.fernet import Fernet as _Fernet
import bcrypt as _bcrypt
import uuid as _uuid
# own code
from src.logger_config import setup_logger as _setup_logger
from src.const import ENV_PATH as _ENV_PATH

class CryptManager:
    def __init__(self):
        self.__logger = _setup_logger(__name__)  # logger creating
        self.__fernet = None
        self.__logger.debug("Checking env for keys...")
        # download .env before reading data
        
        _load_dotenv(_ENV_PATH)
        key = self.__take_key()
        self.__fernet = _Fernet(key)

    def __take_key(self) -> bytes:
        # func will try to load the key
        # and if there is a problem
        # then will created the new key
        encryption_key = _os.getenv('encryption_key')
        if encryption_key is None:
            self.__logger.info("Keys successfully downloaded")
            return self.__create_key()
        encryption_key = bytes.fromhex(encryption_key)
        return encryption_key

    def __create_key(self, _ENV_PATH: _Path) -> bytes:
        encryption_key = _Fernet.generate_key()
        # save to env with absolute path
        # because env not inside env -_-
        _set_key(str(_ENV_PATH), 'encryption_key', encryption_key.hex())
        self.__logger.info("Keys were created successfully")
        return encryption_key
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
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

    async def verify_password(self, password: str, hashed: str) -> bool:
        return _bcrypt.checkpw(password.encode(), hashed.encode())

    async def generate_session_key(self):
        return ''.join(str(_uuid.uuid4()) for _ in range(7))