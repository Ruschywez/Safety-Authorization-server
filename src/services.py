from pathlib import Path
from datetime import date, timedelta
from typing import List, Optional
import secrets
import bcrypt
"""Import from own code"""
from src.const import EXPIRATION_TIME
from src.repositories import UsrRepository, SessionRepository, SecretRepository
from src.entities import Usr, Session, Secret as Secret
from src.encryption import CryptManager
from src.imageManager import ImageManager
"""More readable import"""
from src.exceptions import UserNotFoundError, WrongPasswordError, AvatarNotFoundError, ConflictError
from src.exceptions import SecretNotFoundError, SecretImageNotFoundError, ValidationError

"""password's methods"""
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

class SessionService:
    def __init__(self, session_repository: SessionRepository, usr_repository: UsrRepository, crypt_manager: CryptManager):
        self.session_repository: SessionRepository = session_repository
        self.usr_repository: UsrRepository = usr_repository
        self.crypt_manager: CryptManager = crypt_manager
    async def is_session_key_valid(self, key: str) -> bool:
        # Check if session is valid (not expired)
        session: Optional[Session] = await self.session_repository.get_by_key(key)
        return session.expires_at >= date.today() if session is not None else False
    
    async def get_user_id(self, key: str) -> int:
        if await self.is_session_key_valid(key):
            user_id: Optional[int] = await self.session_repository.get_user_id_by_key(key)
            if user_id is None:
                raise UserNotFoundError()
            return user_id
        else:
            raise ValueError("Invalid session key")
    async def get_user(self, key: str) -> Usr:
        if await self.is_session_key_valid(key):
            user: Optional[Usr] = await self.session_repository.get_usr(key)
            if user is None:
                raise UserNotFoundError()
            return user
        else:
            raise ValueError("Invalid session key")
    async def authentication(self, login: str, password: str) -> str:
        user: Optional[Usr] = await self.usr_repository.get_by_login(login)
        if user is None:
            raise UserNotFoundError()
        if not verify_password(password=password, hashed=user.password):
            raise WrongPasswordError()
        session: Session = await self.session_repository.create(
            key=secrets.token_urlsafe(192),# 256 symbols in format Base64
            usr=user.id,
            created_at=date.today(),
            expires_at=date.today() + timedelta(days=EXPIRATION_TIME)
        )
        return session.key
    async def logout(self, session_key: str) -> bool:
        return await self.session_repository.delete(session_key)
    async def delete_expired_sessions(self) -> int:
        count = 0
        for session in await self.session_repository.get_expired_sessions(date.today()):
            if await self.session_repository.delete(session.key):
                count += 1
        return count

class UsrService:
    def __init__(self, usr_repository: UsrRepository, session_service: SessionService, crypt_manager: CryptManager, image_manager: ImageManager):
        self.usr_repository: UsrRepository = usr_repository
        self.session_service: SessionService = session_service
        self.crypt_manager: CryptManager = crypt_manager
        self.image_manager: ImageManager = image_manager
    async def register(self, login: str, password: str, email: str) -> Usr:
        # create new user
        login = self.usr_repository.validation_login(login)
        email = self.usr_repository.validation_email(email)
        password = self.usr_repository.validation_password(password)
        if await self.usr_repository.get_by_login(login) is not None:
            raise ConflictError("User with this login already exists")
        if await self.usr_repository.get_by_email(email) is not None:
            raise ConflictError("User with this email already exists")
        password = self.crypt_manager.hash_password(password)
        return await self.usr_repository.create(login=login, password=password, email=email, avatar=None)
    async def update_profile(self, key: str, **kwargs) -> bool:
        # modify existing user without avatar!
        if 'password' in kwargs:
            kwargs['password'] = hash_password(self.usr_repository.validation_password(kwargs['password']))
        if 'email' in kwargs:
            kwargs['email'] = self.usr_repository.validation_email(kwargs['email'])
            if await self.usr_repository.get_by_email(kwargs['email']) is not None:
                raise ConflictError("User with this email already exists")

        user_id: Optional[int] = await self.session_service.get_user_id(key)
        return await self.usr_repository.update(usr=user_id, **kwargs)
    async def delete_user(self, key: str) -> bool:
        # remove user from system
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        return await self.usr_repository.delete(user_id) # is already bool
    async def get_user_info(self, key: str) -> dict:
        # get user information by session key
        user: Usr = await self.session_service.get_user(key)
        return {
            "login": user.login,
            "email": user.email,
            "is_avatar": user.avatar is not None 
        }
    async def set_avatar(self, key: str, avatar: bytes) -> bool:
        # modify existing user's avatar
        # old avatar will be deleted, if it exists, and new one will be set
        user: Optional[Usr] = await self.session_service.get_user(key)
        avatar_path = await self.image_manager.save_avatar_image(avatar)
        return await self.usr_repository.update(usr=user.id, avatar=str(avatar_path))
    async def get_user_avatar(self, key: str) -> bytes:
        # get user avatar by session key
        user: Optional[Usr] = await self.session_service.get_user(key)
        avatar = await self.image_manager.load_avatar_image(Path(user.avatar))
        return avatar
    async def delete_avatar(self, key: str) -> bool:
        # remove user's avatar, but profile will be exist
        user: Optional[Usr] = await self.session_service.get_user(key)
        if user.avatar is not None:
            await self.image_manager.delete_avatar_image(Path(user.avatar))
        return await self.usr_repository.update(usr=user.id, avatar=None) # is already bool
class SecretService:
    def __init__(self, secret_repository: SecretRepository, session_service: SessionService, image_manager: ImageManager, crypt_manager: CryptManager):
        self.secret_repository: SecretRepository = secret_repository
        self.session_service: SessionService = session_service
        self.image_manager: ImageManager = image_manager
        self.crypt_manager: CryptManager = crypt_manager
    async def create_secret(self, key: str, text: str, image: Optional[bytes]=None) -> Secret:
        # create new secret for user with text and optional image
        if not text: raise ValidationError(detail="Text cannot be empty or None!")
        image_path: Optional[Path] = await self.image_manager.save_secret_image(image) if image is not None else None
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        encrypted_text: str = self.crypt_manager.encrypt(text)
        return await self.secret_repository.create(
            usr=user_id,
            text=encrypted_text,
            image_path=str(image_path) if image is not None else None
            )
    async def get_secrets(self, key: str) -> List[dict]:
        # get all secrets of user
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        secrets: List[Secret] = await self.secret_repository.get_by_usr(user_id)
        return [{
                "id": secret.id,
                "text": await self.crypt_manager.decrypt(secret.text),
                "has_image": secret.image_path is not None # boolean! hell yeah
            }for secret in secrets]
    async def delete_secret(self, key: str, secret_id: int) -> bool:
        # remove secret from system
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        secret: Optional[Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise SecretNotFoundError()
        return await self.secret_repository.delete(secret_id) # is already bool
    async def update_secret(self, key: str, secret_id: int, text: str) -> bool:
        # modify existing secret's text
        if text is not None and not text:
            raise ValidationError("Text cannot be empty or None!")
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        secret: Optional[Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id: raise SecretNotFoundError()
        encrypted_text: str = await self.crypt_manager.encrypt(text) if text is not None else None
        return await self.secret_repository.update(secret=secret_id, text=encrypted_text) # is already bool
    async def get_secret_image(self, key: str, secret_id: int) -> bytes:
        # get secret's image by secret's id
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        if user_id is None: raise UserNotFoundError()
        secret: Optional[Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise SecretNotFoundError("Secret not found")
        if secret.image_path is None:
            raise SecretImageNotFoundError("Secret has no image")
        return await self.image_manager.load_secret_image(Path(secret.image_path))
    async def set_secret_image(self, key: str, secret_id: int, image: bytes) -> bool:
        # set secret's image, don't matter if it exists or not, because it will be replaced
        # but if it exists, then need delete old image
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        secret: Optional[Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise SecretNotFoundError()
        if secret.image_path is not None:
            await self.image_manager.delete_secret_image(Path(secret.image_path))
        image_path: Path = await self.image_manager.save_secret_image(image)
        return await self.secret_repository.update(secret=secret_id, image_path=str(image_path)) # is already bool
    async def remove_secret_image(self, key: str, secret_id: int) -> bool:
        # remove secret's image, but text will be exist
        user_id: Optional[int] = await self.session_service.get_user_id(key)
        secret: Optional[Secret] = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise SecretNotFoundError()
        await self.image_manager.delete_secret_image(Path(secret.image_path))
        return await self.secret_repository.update(secret=secret_id, image_path=None) # is already bool