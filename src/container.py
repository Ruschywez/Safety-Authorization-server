from src.const import DB_URL
from src.encryption import CryptManager
from src.imageManager import ImageManager
from src.repositories import UsrRepository, SessionRepository, SecretRepository
from src.services import UsrService, SessionService, SecretService

from peewee_aio import Manager as _Manager

crypt_manager = CryptManager()
image_manager = ImageManager(crypt_manager)

usr_repository = UsrRepository(crypt_manager)
session_repository = SessionRepository(crypt_manager)
secret_repository = SecretRepository(crypt_manager)

usr_service = UsrService(usr_repository, session_repository, crypt_manager, image_manager)
session_service = SessionService(session_repository, usr_repository, crypt_manager)
secret_service = SecretService(secret_repository, session_repository, image_manager, crypt_manager)


def get_manager():
    return _Manager(DB_URL)

def get_crypt_manager():
    return crypt_manager

def get_image_manager():
    return image_manager

def get_usr_repository():
    return usr_repository

def get_session_repository():
    return session_service

def get_secret_repository():
    return secret_service

def get_session_service():
    return session_service

def get_usr_service():
    return usr_service

def get_secret_service():
    return secret_service
