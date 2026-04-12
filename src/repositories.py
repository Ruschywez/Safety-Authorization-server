from peewee_aio import Manager
from src.entities import  Usr, Session, Secret
from typing import Optional, List, Union
from datetime import date

class UsrRepository:
    def __init__(self, manager: Manager, model: Usr):
        self.manager: Manager = manager
        self.model: Usr = model
    async def get_by_id(self, id: int) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Usr]:
        query = self.model.select()
        result = await self.manager.fetchall(query)
        return result
    async def get_by_login(self, login: str) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str, avatar: str="") -> Usr:
        if login is None:
            raise ValueError('Login cannot be None')
        if password is None:
            raise ValueError('Password cannot be None')
        if email is None:
            raise ValueError('Email cannot be None')
        return await self.manager.create(self.model, login=login.strip().lower(), password=password, email=email.strip().lower(), avatar=avatar)
    async def update_fields(self, usr: Union[int,Usr], **kwargs) -> bool:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if 'login' in kwargs and isinstance(kwargs['login'], str):
            kwargs['login'] = kwargs['login'].strip().lower()
        if 'email' in kwargs and isinstance(kwargs['email'], str):
            kwargs['email'] = kwargs['email'].strip().lower()
        if isinstance(usr, Usr):
            query = self.model.update(**kwargs).where(self.model.id==usr.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==usr)
        return await self.manager.execute(query) > 0 # bool!
    async def update(self, usr: Union[int,Usr], **kwargs) -> Optional[Usr]:
        if 'id' in kwargs: # validation
            raise ValueError("Cannot update primary key 'id'")
        if 'login' in kwargs and isinstance(kwargs['login'],str):
            kwargs['login'] = kwargs['login'].strip().lower()
        if 'email' in kwargs and isinstance(kwargs['email'], str):
            kwargs['email'] = kwargs['email'].strip().lower()
        if isinstance(usr, Usr):
            query = self.model.update(**kwargs).where(self.model.id==usr.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id==usr)
        rows = await self.manager.execute(query) # update process...
        if rows:
            return await self.get_by_id(usr.id)
        return None
    async def delete(self, usr: Union[Usr, int]) -> bool:
        if isinstance(usr, Usr):
            query = self.model.delete().where(self.model.id == usr.id)
        else:
            query = self.model.delete().where(self.model.id == usr)
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
        return await list(self.manager.fetchall(query))
    async def get_expired_sessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at < date)
        return await list(self.manager.fetchall(query))
    async def get_active_sessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at >= date)
        return await list(self.manager.fetchall(query))
    async def get_by_Usr(self, usr: Union[Usr, int]) -> List[Session]:
        if isinstance(usr, Usr):
            query = self.model.select().where(self.model.Usr_id == usr.id)
        else:
            query = self.model.select().where(self.model.Usr_id == usr)
        return await self.manager.fetchall(query)
    async def create(self, key: str, usr: Union[int, Usr], created_at: date, expires_at: date) -> Session:
        return await self.manager.create(self.model, key=key, Usr_id=usr, created_at=created_at, expires_at=expires_at)
    async def delete(self, key: str) -> bool:
        query = self.model.delete().where(self.model.key == key)
        return await self.manager.execute(query) > 0

class SecretRepository:
    def __init__(self, manager: Manager, model: Secret):
        self.manager = manager
        self.model = model
    async def get_by_id(self, id: int) -> Optional[Secret]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Secret]:
        query = self.model.select()
        return await self.manager.fetchall(query)
    async def get_by_Usr(self, usr: Union[int, Usr]) -> List[Secret]:
        if isinstance(usr, Usr):
            query = self.model.select().where(self.model.Usr_id == usr.id)
        else:
            query = self.model.select().where(self.model.Usr_id == usr)
        return await self.manager.fetchall(query)
    async def create(self, usr: Union[int, Usr], text: str, image_path: Union[str, None]) -> Secret:
        if image_path is None:
            return await self.manager.create(self.model, Usr_id=usr, text=text)
        else:
            return await self.manager.create(self.model, Usr_id=usr, text=text, image_path=image_path)
    async def update_fields(self, secret: Union[int, Secret], **kwargs) -> bool:
        if 'text' in kwargs and isinstance(kwargs['text'], str):
            kwargs['text'] = kwargs['text'].strip()
        if 'image_path' in kwargs and isinstance(kwargs['image_path'], str):
            kwargs['image_path'] = kwargs['image_path'].strip()
        if isinstance(secret, Secret):
            query = self.model.update(**kwargs).where(self.model.id == secret.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id == secret)
        return await self.manager.execute(query) > 0
    async def update(self, secret: Union[int, Secret], **kwargs) -> Optional[Secret]:
        if 'text' in kwargs and isinstance(kwargs['text'], str):
            kwargs['text'] = kwargs['text'].strip()
        if 'image_path' in kwargs and isinstance(kwargs['image_path'], str):
            kwargs['image_path'] = kwargs['image_path'].strip()
        if isinstance(secret, Secret):
            query = self.model.update(**kwargs).where(self.model.id == secret.id)
        else:
            query = self.model.update(**kwargs).where(self.model.id == secret)
        rows = await self.manager.execute(query) # update process...
        if rows:
            return await self.get_by_id(secret.id)
        return None
    async def delete(self, secret: Union[Secret, int]) -> bool:
        if isinstance(secret, Secret):
            query = self.model.delete().where(self.model.id == secret.id)
        else:
            query = self.model.delete().where(self.model.id == secret)
        return await self.manager.execute(query) > 0