from entities import BaseModel, User, Secret, Session
from peewee_aio import Manager
import asyncio
from entities import BaseModel, User, Session, Secret
from db_connect import take_db_connect
from typing import Optional, List, Union
from peewee import DoesNotExist

class UserRepository:
    def __init__(self, manager: Manager):
        self.manager: Manager = manager
        self.model = User
    async def get_by_id(self, id: Union[int, str]) -> Optional[User]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[User]:
        query = self.model.select()
        return await self.manager.execute(query)
    async def get_by_login(self, login: str) -> Optional[User]:
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str, avatar: str|None=None) -> User:
        return await self.manager.create(self.model, login=login, password=password, email=email, avatar=avatar)
    async def update_fields(self, user: Union[str,int,User], **kwargs) -> bool:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if isinstance(user, User):
            query = self.model.update(**kwargs).where(self.model.id==user.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==user)
        return await self.manager.execute(query) > 0 # bool!
    async def update(self, user: Union[str,int,User], **kwargs) -> Optional[User]:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if isinstance(user, User):
            query = self.model.update(**kwargs).where(self.model.id==user.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==user)
        rows = await self.manager.execute(query) # update process...
        if rows:
            return await self.get_by_id(user)
        return None