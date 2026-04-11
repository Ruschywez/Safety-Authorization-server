from peewee_aio import Manager
import asyncio
from entities import BaseModel, User, Session, Secret
from db_connect import take_db_connect
from typing import Optional, List, Union
from datetime import date
import peewee

class UserRepository:
    def __init__(self, manager: Manager, model: User):
        self.manager: Manager = manager
        self.model: User = model
    async def get_by_id(self, id: int) -> Optional[User]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[User]:
        query = self.model.select()
        return await list(self.manager.execute(query))
    async def get_by_login(self, login: str) -> Optional[User]:
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str, avatar: str="") -> User:
        if login is None:
            raise ValueError('Login cannot be None')
        if password is None:
            raise ValueError('Password cannot be None')
        if email is None:
            raise ValueError('Email cannot be None')
        return await self.manager.create(self.model, login=login.strip().lower(), password=password, email=email.strip().lower(), avatar=avatar)
    async def update_fields(self, user: Union[int,User], **kwargs) -> bool:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if 'login' in kwargs and isinstance(kwargs['login'], str):
            kwargs['login'] = kwargs['login'].strip().lower()
        if 'email' in kwargs and isinstance(kwargs['email'], str):
            kwargs['email'] = kwargs['email'].strip().lower()
        if isinstance(user, User):
            query = self.model.update(**kwargs).where(self.model.id==user.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==user)
        return await self.manager.execute(query) > 0 # bool!
    async def update(self, user: Union[int,User], **kwargs) -> Optional[User]:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if 'login' in kwargs and isinstance(kwargs['login'],str):
            kwargs['login'] = kwargs['login'].strip().lower()
        if 'email' in kwargs and isinstance(kwargs['email'], str):
            kwargs['email'] = kwargs['email'].strip().lower()
        if isinstance(user, User):
            query = self.model.update(**kwargs).where(self.model.id==user.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==user)
        rows = await self.manager.execute(query) # update process...
        if rows:
            return await self.get_by_id(user)
        return None
    async def delete(self, user: Union[User, int]) -> bool:
        if isinstance(user, User):
            query = self.model.delete().where(self.model.id == user.id)
        else:
            query = self.model.delete().where(self.model.id == user)
        return await self.manager.execute(query) > 0
class SessionRepository:
    def __init__(self, manager: Manager, model: Session):
        self.manager: Manager = manager
        self.model: Session = model
    async def get_by_key(self, key: str) -> Optional[Session]:
        # Primary key of Session class has name "key", not the "id"
        return await self.manager.get_or_none(self.model, key=key)
    async def get_all(self) -> List[Session]:
        query = self.model.select()
        return await list(self.manager.execute(query))
    async def get_expired_sessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at < date)
        return await list(self.manager.execute(query))
    async def get_active_sessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at >= date)
        return await list(self.manager.execute(query))
    async def get_by_user(self, user: Union[User, int]) -> List[Session]:
        if isinstance(user, User):
            query = self.model.select().where(self.model.user_id == user.id)
        else:
            query = self.model.select().where(self.model.user_id == user)
        return await list(self.manager.execute(query))
    async def create(self, key: str, user: Union[int, User], created_at: date, expires_at: date) -> Session:
        return await self.manager.create(self.model, key=key, user_id=user, created_at=created_at, expires_at=expires_at)
    async def delete(self, key: str) -> bool:
        query = self.model.delete().where(self.model.key == key)
        return await self.manager.execute(query) > 0

class SecretRepository:
    def __init__(self, manager: Manager, model: Secret):
        self.manager = manager
        self.model = model
    async def get_by_id(self, id: int) -> Secret:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Secret]:
        query = self.model.select()
        return await list(self.manager.execute(query))
    async def get_by_user(self, user: Union[int, User]) -> List[Secret]:
        if isinstance(user, User):
            query = self.model.select().where(self.model.user_id == user.id)
        else:
            query = self.model.select().where(self.model.id == user)
        return await list(self.manager.execute(query))
    async def create(self, user: Union[int, User], text: str, image_path: Union[str, None]) -> Secret:
        if image_path is None:
            return await self.manager.create(self.model, user_id=user, text=text)
        else:
            return await self.manager.create(self.model, user_id=user, text=text, image_path=image_path)