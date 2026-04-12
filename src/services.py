from pathlib import Path
import uuid
from src.repositories import UsrRepository, SessionRepository, SecretRepository
from src.entities import Usr, Session, Secret
from src.encryption import CryptManager
from src.imageManager import ImageManager
from datetime import date, timedelta
from typing import List, Optional
from fastapi import HTTPException, status

class SessionService:
    def __init__(self, session_repository: SessionRepository, usr_repository: UsrRepository, crypt_manager: CryptManager):
        self.session_repository = session_repository
        self.usr_repository = usr_repository
        self.crypt_manager = crypt_manager
    async def is_session_key_valid(self, key: str) -> bool:
        # Check if session is valid (not expired)
        session: Optional[Session] = await self.session_repository.get_by_key(key)
        if session is None:
            return False
        else:
            return session.expires_at >= date.today()
    async def get_user_id(self, key: str) -> int:
        if await self.is_session_key_valid(key):
            user_id = await self.session_repository.get_user_id_by_key(key)
            if user_id is None:
                raise ValueError("Not found")
            return user_id
        else:
            raise ValueError("Invalid session key")
    async def authentication(self, login: str, password: str) -> str:
        """
            if usr with login exists, if password is correct -> new session
        """
        user = await self.usr_repository.get_by_login(login)
        if user is None:
            # user not found
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this login does not exist")
        if not self.crypt_manager.verify_password(password=password, hashed=user.password):
            # incorrect password
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
        session: Session = await self.session_repository.create(
            key=''.join(str(uuid.uuid4()) for _ in range(7)),
            usr=user.id,
            created_at=date.today(),
            expires_at=date.today() + timedelta(days=30)
        )
        return session.key
    async def logout(self, session_key: str) -> bool:
        # delete session by key
        return await self.session_repository.delete(session_key)
    async def delete_expired_sessions(self) -> int:
        # delete sessions by date
        expired_sessions = await self.session_repository.get_expired_sessions(date.today())
        count = 0
        for session in expired_sessions:
            # not a transaction bruh
            if await self.session_repository.delete(session.key):
                count += 1
        return count

class UsrService:
    def __init__(self, usr_repository: UsrRepository, session_service: SessionService, crypt_manager: CryptManager, image_manager: ImageManager):
        self.usr_repository = usr_repository
        self.session_service = session_service
        self.crypt_manager = crypt_manager
        self.image_manager = image_manager
    async def register(self, login: str, password: str, email: str) -> Usr:
        # create new user
        if await self.usr_repository.get_by_login(login) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this login already exists")
        if await self.usr_repository.get_by_email(email) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
        if password is None or len(password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        password = await self.crypt_manager.hash_password(password)
        return await self.usr_repository.create(login=login, password=password, email=email, avatar=None)
    async def update_profile(self, key: str, **kwargs) -> bool:
        # modify existing user without avatar!
        if 'password' in kwargs:
            if kwargs['password'] is None or len(kwargs['password']) < 8:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
            kwargs['password'] = await self.crypt_manager.hash_password(kwargs['password'])
        user_id = await self.session_service.get_user_id(key)
        return await self.usr_repository.update_fields(usr=user_id, **kwargs)
    async def update_avatar(self, key: str, avatar: bytes) -> bool:
        # modify existing user's avatar
        # old avatar will be deleted, if it exists, and new one will be set
        user_id = await self.session_service.get_user_id(key)
        user = await self.usr_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.avatar is not None:
            await self.image_manager.delete_avatar_image(Path(user.avatar))
        avatar_path = await self.image_manager.save_avatar_image(avatar)
        return await self.usr_repository.update_fields(usr=user_id, avatar=str(avatar_path))
    async def delete_user(self, key: str) -> bool:
        # remove user from system
        user_id = await self.session_service.get_user_id(key)
        return await self.usr_repository.delete(user_id) # is already bool
    async def get_user_info(self, key: str) -> dict:
        # get user information by session key
        user_id = await self.session_service.get_user_id(key)
        user = await self.usr_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "login": user.login,
            "email": user.email,
            "is_avatar": user.avatar is not None 
        }
    async def get_user_avatar(self, key: str) -> bytes:
        # get user avatar by session key
        user_id = await self.session_service.get_user_id(key)
        user = await self.usr_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.avatar is None:
            raise HTTPException(status_code=404, detail="User has no avatar")
        return await self.image_manager.load_avatar_image(Path(user.avatar))



class SecretService:
    def __init__(self, secret_repository: SecretRepository, session_service: SessionService, image_manager: ImageManager, crypt_manager: CryptManager):
        self.secret_repository = secret_repository
        self.session_service = session_service
        self.image_manager = image_manager
        self.crypt_manager = crypt_manager

    async def create_secret(self, key: str, text: str, image: Optional[bytes]=None) -> Secret:
        # create new secret for user with text and optional image
        if not text: # for bad request, coz text is not null
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty or None!")

        user_id = await self.session_service.get_user_id(key)
        if image is not None:
            image_path = await self.image_manager.save_secret_image(image)
            encrypted_text = self.crypt_manager.encrypt(text)
            return await self.secret_repository.create(usr=user_id, text=encrypted_text, image_path=str(image_path))
        else:
            return await self.secret_repository.create(usr=user_id, text=text, image_path=None)
    async def get_secrets(self, key: str) -> List[dict]:
        # get all secrets of user
        user_id = await self.session_service.get_user_id(key)
        secrets = await self.secret_repository.get_by_Usr(user_id)
        return [
            {
                "id": secret.id,
                "text": await self.crypt_manager.decrypt(secret.text),
                "has_image": secret.image_path is not None # boolean! hell yeah
            }
            for secret in secrets
        ]
    async def get_secret_image(self, key: str, secret_id: int) -> bytes:
        # get secret's image by secret's id
        user_id = await self.session_service.get_user_id(key)
        secret = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        if secret.image_path is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret has no image")
        return await self.image_manager.load_secret_image(Path(secret.image_path))
    async def delete_secret(self, key: str, secret_id: int) -> bool:
        # remove secret from system
        user_id = await self.session_service.get_user_id(key)
        secret = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        return await self.secret_repository.delete(secret_id) # is already bool
    async def update_secret(self, key: str, secret_id: int, text: str) -> bool:
        # modify existing secret's text
        if text is not None and not text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty or None!")
        user_id = await self.session_service.get_user_id(key)
        secret = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        encrypted_text = await self.crypt_manager.encrypt(text) if text is not None else None
        return await self.secret_repository.update_fields(secret=secret_id, text=encrypted_text) # is already bool
    async def set_secret_image(self, key: str, secret_id: int, image: bytes) -> bool:
        # set secret's image, don't metter if it exists or not, because it will be replaced
        # but if it exists, then need delete old image
        user_id = await self.session_service.get_user_id(key)
        secret = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        if secret.image_path is not None:
            await self.image_manager.delete_secret_image(Path(secret.image_path))
        image_path = await self.image_manager.save_secret_image(image)
        return await self.secret_repository.update_fields(secret=secret_id, image_path=str(image_path)) # is already bool
    async def remove_secret_image(self, key: str, secret_id: int) -> bool:
        # remove secret's image, but text will be exist
        user_id = await self.session_service.get_user_id(key)
        secret = await self.secret_repository.get_by_id(secret_id)
        if secret is None or secret.user_id.id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        if secret.image_path is not None:
            await self.image_manager.delete_secret_image(Path(secret.image_path))
        return await self.secret_repository.update_fields(secret=secret_id, image_path=None) # is already bool