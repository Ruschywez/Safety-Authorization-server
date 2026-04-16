import os
from dotenv import load_dotenv as load_dotenv, set_key
from cryptography.fernet import Fernet
# own code
from src.const import ENV_PATH

class CryptManager:
    def __init__(self):
        # download .env before reading data
        load_dotenv(ENV_PATH)
        key = self.__take_key()
        self.__fernet = Fernet(key)

    def __take_key(self) -> bytes:
        # func will try to load the key
        # and if there is a problem
        # then will created the new key
        encryption_key = os.getenv('encryption_key')
        if encryption_key is None:
            return self.__create_key()
        encryption_key = bytes.fromhex(encryption_key)
        return encryption_key

    def __create_key(self) -> bytes:
        encryption_key = Fernet.generate_key()
        # save to env with absolute path
        # because env not inside env -_-
        set_key(str(ENV_PATH), 'encryption_key', encryption_key.hex())
        return encryption_key
    """encrypt&decrypt data methods"""
    def encrypt(self, text: str) -> str:
        if not text:
            raise ValueError("Text cannot be empty or None!")
        # str -> bytes -> encrypt -> bytes -> str
        return self.__fernet.encrypt(text.encode()).decode()

    def decrypt(self, text: str) -> str:
        # str -> bytes -> decrypt -> bytes -> str
        return self.__fernet.decrypt(text.encode()).decode()
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        if not data:
            raise ValueError("Data cannot be empty or None!")
        # bytes -> encrypt -> bytes
        return self.__fernet.encrypt(data)

    def decrypt_bytes(self, data: bytes) -> bytes:
        # bytes -> decrypt -> bytes
        return self.__fernet.decrypt(data)