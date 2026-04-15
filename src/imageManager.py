from pathlib import Path
import uuid 
from src.exceptions import AvatarNotFoundError, SecretImageNotFoundError
from src.encryption import CryptManager
from src.const import AVATAR_PATH, SECRET_PATH

class ImageManager:
    def __init__(self, crypt_manager: CryptManager):
        self.crypt_manager: CryptManager = crypt_manager
        self.avatar_save_path: Path = AVATAR_PATH
        self.secret_save_path: Path = SECRET_PATH

    async def generate_random_avatar_name(self) -> str:
        name = ''.join(str(uuid.uuid4()) for _ in range(6)) + ".png"
        if not await self.is_unique_avatar_image_name(name):
            return await self.generate_random_avatar_name()
        else:
            return name
    async def generate_random_secret_image_name(self) -> str:
        name = ''.join(str(uuid.uuid4()) for _ in range(6)) + ".png"
        if not await self.is_unique_secret_image_name(name):
            return await self.generate_random_secret_image_name()
        else:
            return name
    async def is_unique_avatar_image_name(self, name: str) -> bool:
        avatar_path = self.avatar_save_path / name
        return not avatar_path.exists()  
    async def is_unique_secret_image_name(self, name: str) -> bool:
        secret_path = self.secret_save_path / name
        return not secret_path.exists()

    async def save_avatar_image(self, avatar: bytes) -> Path:
        # avatar not needs to be encrypted because it's not a secret
        name = await self.generate_random_avatar_name()
        filepath = self.avatar_save_path / name
        with open(filepath, 'wb') as f:
            f.write(avatar)
        return filepath

    async def save_secret_image(self, secret: bytes) -> Path:
        # secret image needs to be encrypted because it's a secret
        name = await self.generate_random_secret_image_name()
        filepath = self.secret_save_path / name
        encrypted_secret = await self.crypt_manager.encrypt_bytes(secret)
        with open(filepath, 'wb') as f:
            f.write(encrypted_secret)
        return filepath

    async def load_avatar_image(self, avatar: Path) -> bytes:
        filepath = self.avatar_save_path / avatar
        if not filepath.exists():
            raise AvatarNotFoundError()
        with open(filepath, 'rb') as f:
            return f.read()
    
    async def load_secret_image(self, secret: Path) -> bytes:
        # need encrypted secret image to decrypt it
        filepath = self.secret_save_path / secret
        if not filepath.exists():
            raise SecretImageNotFoundError()
        with open(filepath, 'rb') as f:
            secret = f.read()
        return await self.crypt_manager.decrypt_bytes(secret)
    async def delete_avatar_image(self, avatar: Path) -> bool:
        filepath = self.avatar_save_path / avatar
        if not filepath.exists():
            raise AvatarNotFoundError()
        filepath.unlink()
        return True
    async def delete_secret_image(self, secret: Path) -> bool:
        filepath = self.secret_save_path / secret
        if not filepath.exists():
            raise SecretImageNotFoundError()
        filepath.unlink()
        return True