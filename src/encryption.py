import os
from pathlib import Path
import secrets
from logger_config import setup_logger
import dotenv

class CryptManager:
    def __init__(self):
        self.logger = setup_logger(__name__)
        """if we don't have a key we need create it!"""
        self.logger.debug("Checking env for keys...")
        if Path(".env").exists and self.__is_keys_exists():
            self.__keys = self.__load_keys()
            self.logger.info("Keys successfully downloaded")
        else:
            self.logger.warning("keys is not found!")
            self.__keys = self.__first_run()
            self.logger.info("Keys were created successfully")
            
        
    def __load_keys(self) -> dict:
        pass
    def __first_run(self) -> dict:
        keys = {
            'encryption_key': self.__generate_fernet_ket(),
            'hmac_key': self.__generate_crypto_random_key(32),
            'jwt_secret': self.__generate_crypto_random_key(64),
            'api_key_salt': self.__generate_crypto_random_key(16)
        }
        # save to env yo
        for key, value in keys.items():
            dotenv.set_key('.env', key, value)
        return keys
    def __is_keys_exists(self) -> bool:
        pass