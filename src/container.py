from src.const import DB_URL as _DB_URL
from src.encryption import CryptManager as _CryptManager
from src.imageManager import ImageManager as _ImageManager
from src.entities import Usr as _Usr, Session as _Session, Secret as _Secret
from src.repositories import UsrRepository as _UsrRepository, SessionRepository as _SessionRepository, SecretRepository as _SecretRepository
from src.services import UsrService as _UsrService, SessionService as _SessionService, SecretService as _SecretService

from peewee_aio import Manager as _Manager

_crypt_manager = _CryptManager()
_image_manager = _ImageManager(_crypt_manager)

_usr_repository = _UsrRepository(_crypt_manager)
_session_repository = _SessionRepository(_crypt_manager)
_secret_repository = _SecretRepository(_crypt_manager)

_usr_service = _UsrService(_usr_repository, _session_repository, _crypt_manager, _image_manager)
_session_service = _SessionService(_session_repository, _usr_repository, _crypt_manager)
_secret_service = _SecretService(_secret_repository, _session_repository, _image_manager, _crypt_manager)


def get_manager():
    return _Manager(_DB_URL)

def get_crypt_manager():
    return _crypt_manager

def get_image_manager():
    return _image_manager

def get_usr_repository():
    return _usr_repository

def get_session_repository():
    return _session_service

def get_secret_repository():
    return _secret_service

def get_session_service():
    return _session_service

def get_usr_service():
    return _usr_service

def get_secret_service():
    return _secret_service
