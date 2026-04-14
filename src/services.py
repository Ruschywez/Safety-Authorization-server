from pathlib import Path as _Path
from datetime import date as _date, timedelta as _timedelta
from typing import List as _List, Optional as _Optional
"""Import from own code"""
from src.const import EXPIRATION_TIME as _EXPIRATION_TIME
from src.repositories import UsrRepository as _UsrRepository, SessionRepository as _SessionRepository, SecretRepository as _SecretRepository
from src.entities import Usr as _Usr, Session as _Session, Secret as _Secret
from src.encryption import CryptManager as _CryptManager
from src.imageManager import ImageManager as _ImageManager
"""More readable import"""
from src.exceptions import UserNotFoundError as _UserNotFoundError, WrongPasswordError as _WrongPasswordError
from src.exceptions import AvatarNotFoundError as _AvatarNotFoundError, ConflictError as _ConflictError
from src.exceptions import SecretNotFoundError as _SecretNotFoundError, SecretImageNotFoundError as _SecretImageNotFoundError
from src.exceptions import ValidationError as _ValidationError

class SessionService:
    def __init__(self, session_repository: _SessionRepository, usr_repository: _UsrRepository, crypt_manager: _CryptManager):
        self.session_repository: _SessionRepository = session_repository
        self.usr_repository: _UsrRepository = usr_repository
        self.crypt_manager: _CryptManager = crypt_manager
    async def is_session_key_valid(self, key: str) -> bool:
        # Check if session is valid (not expired)
        session: _Optional[_Session] = await self.session_repository.get_by_key(key)
        return session.expires_at >= _date.today() if session is not None else False
    
    async def get_user_id(self, key: str) -> int:
        if await self.is_session_key_valid(key):
            user_id: _Optional[int] = await self.session_repository.get_user_id_by_key(key)
            if user_id is None: raise _UserNotFoundError()
            return user_id
        else: raise ValueError("Invalid session key")
    async def get_user(self, key: str) -> _Usr:
        if await self.is_session_key_valid(key):
            user: _Optional[_Usr] = await self.session_repository.get_usr(key)
            if user is None: raise _UserNotFoundError()
            return user
        else: raise ValueError("Invalid session key")
    async def authentication(self, login: str, password: str) -> str:
        user: _Optional[_Usr] = await self.usr_repository.get_by_login(login)
        if user is None: raise _UserNotFoundError()
        if not self.crypt_manager.verify_password(password=password, hashed=user.password): raise _WrongPasswordError()
        session: _Session = await self.session_repository.create(
            key=self.crypt_manager.generate_session_key(),
            usr=user.id,
            created_at=_date.today(),
            expires_at=_date.today() + _timedelta(days=_EXPIRATION_TIME)
        )
        return session.key
    async def logout(self, session_key: str) -> bool:
        return await self.session_repository.delete(session_key)
    async def delete_expired_sessions(self) -> int:
        count = 0
        for session in await self.session_repository.get_expired_sessions(_date.today()):
            if await self.session_repository.delete(session.key):
                count += 1
        return count

class UsrService:
    def __init__(self, usr_repository: _UsrRepository, session_service: SessionService, crypt_manager: _CryptManager, image_manager: _ImageManager):
        self.usr_repository: _UsrRepository = usr_repository
        self.session_service: SessionService = session_service
        self.crypt_manager: _CryptManager = crypt_manager
        self.image_manager: _ImageManager = image_manager
    async def register(self, login: str, password: str, email: str) -> _Usr:
        # create new user
        if await self.usr_repository.get_by_login(login) is not None: raise _ConflictError("User with this login already exists")
        if await self.usr_repository.get_by_email(email) is not None: raise _ConflictError("User with this email already exists")
        if password is None or len(password) < 8:                     raise _ValidationError("Password must be at least 8 characters long")
        
        password = await self.crypt_manager.hash_password(password)
        return await self.usr_repository.create(login=login, password=password, email=email, avatar=None)
    async def update_profile(self, key: str, **kwargs) -> bool:
        # modify existing user without avatar!
        if 'password' in kwargs: kwargs['password'] = await self.crypt_manager.hash_password(kwargs['password'])
        if 'email' in kwargs and await self.usr_repository.get_by_email(kwargs['email']) is not None: raise _ConflictError("User with this email already exists")

        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        return await self.usr_repository.update(usr=user_id, **kwargs)
    async def delete_user(self, key: str) -> bool:
        # remove user from system
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        return await self.usr_repository.delete(user_id) # is already bool
    async def get_user_info(self, key: str) -> dict:
        # get user information by session key
        user: _Usr = await self.session_service.get_user(key)
        if user is None: raise _UserNotFoundError()
        return {
            "login": user.login,
            "email": user.email,
            "is_avatar": user.avatar is not None 
        }
    async def set_avatar(self, key: str, avatar: bytes) -> bool:
        # modify existing user's avatar
        # old avatar will be deleted, if it exists, and new one will be set
        user: _Optional[_Usr] = await self.session_service.get_user(key)
        if user is None: raise _UserNotFoundError()
        if user.avatar is not None: await self.image_manager.delete_avatar_image(_Path(user.avatar))
        avatar_path = await self.image_manager.save_avatar_image(avatar)
        return await self.usr_repository.update(usr=user.id, avatar=str(avatar_path))
    async def get_user_avatar(self, key: str) -> bytes:
        # get user avatar by session key
        user: _Optional[_Usr] = await self.session_service.get_user(key)
        if user is None: raise _UserNotFoundError()
        if user.avatar is None: raise _UserNotFoundError()
        avatar = await self.image_manager.load_avatar_image(_Path(user.avatar))
        if avatar is None: raise _AvatarNotFoundError()
        return avatar
    async def delete_avatar(self, key: str) -> bool:
        # remove user's avatar, but profile will be exist
        user: _Optional[_Usr] = await self.session_service.get_user(key)
        if user is None: raise _UserNotFoundError()
        if user.avatar is not None: await self.image_manager.delete_avatar_image(_Path(user.avatar))
        return await self.usr_repository.update(usr=user.id, avatar=None) # is already bool
class SecretService:
    def __init__(self, secret_repository: _SecretRepository, session_service: SessionService, image_manager: _ImageManager, crypt_manager: _CryptManager):
        self.secret_repository: _SecretRepository = secret_repository
        self.session_service: SessionService = session_service
        self.image_manager: _ImageManager = image_manager
        self.crypt_manager: _CryptManager = crypt_manager
    async def create_secret(self, key: str, text: str, image: _Optional[bytes]=None) -> _Secret:
        # create new secret for user with text and optional image
        if not text: raise _ValidationError(detail="Text cannot be empty or None!")
        image_path: _Optional[_Path] = await self.image_manager.save_secret_image(image) if image is not None else None
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        encrypted_text: str = self.crypt_manager.encrypt(text)
        return await self.secret_repository.create(
            usr=user_id,
            text=encrypted_text,
            image_path=str(image_path) if image is not None else None
            )
    async def get_secrets(self, key: str) -> _List[dict]:
        # get all secrets of user
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        secrets: _Optional[_Secret] = await self.secret_repository.get_by_Usr(user_id)
        if secrets is None: raise _SecretNotFoundError()
        return [{
                "id": secret.id,
                "text": await self.crypt_manager.decrypt(secret.text),
                "has_image": secret.image_path is not None # boolean! hell yeah
            }for secret in secrets]
    async def delete_secret(self, key: str, secret_id: int) -> bool:
        # remove secret from system
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: return _UserNotFoundError()
        secret: _Optional[_Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise _SecretNotFoundError()
        return await self.secret_repository.delete(secret_id) # is already bool
    async def update_secret(self, key: str, secret_id: int, text: str) -> bool:
        # modify existing secret's text
        if text is not None and not text: raise _ValidationError("Text cannot be empty or None!")
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        secret: _Optional[_Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise _SecretNotFoundError()
        encrypted_text: str = await self.crypt_manager.encrypt(text) if text is not None else None
        return await self.secret_repository.update(secret=secret_id, text=encrypted_text) # is already bool
    async def get_secret_image(self, key: str, secret_id: int) -> bytes:
        # get secret's image by secret's id
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        secret: _Optional[_Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise _SecretNotFoundError("_Secret not found")
        if secret.image_path is None: raise _SecretImageNotFoundError("_Secret has no image")
        return await self.image_manager.load_secret_image(_Path(secret.image_path))
    async def set_secret_image(self, key: str, secret_id: int, image: bytes) -> bool:
        # set secret's image, don't matter if it exists or not, because it will be replaced
        # but if it exists, then need delete old image
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        secret: _Optional[_Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise _SecretNotFoundError()
        if secret.image_path is not None: await self.image_manager.delete_secret_image(_Path(secret.image_path))
        image_path: _Path = await self.image_manager.save_secret_image(image)
        return await self.secret_repository.update(secret=secret_id, image_path=str(image_path)) # is already bool
    async def remove_secret_image(self, key: str, secret_id: int) -> bool:
        # remove secret's image, but text will be exist
        user_id: _Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise _UserNotFoundError()
        secret: _Optional[_Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise _SecretNotFoundError()
        if secret.image_path is not None: await self.image_manager.delete_secret_image(_Path(secret.image_path))
        else: raise _SecretImageNotFoundError()
        return await self.secret_repository.update(secret=secret_id, image_path=None) # is already bool