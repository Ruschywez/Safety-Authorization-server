from peewee_aio import Manager
from typing import Optional, List, Union
from datetime import date
# own code
from src.entities import Usr, Session, Secret
from src.const import EMAIL_RE_PATTERN as EMAIL_RE_PATTERN

class UsrRepository:
    def __init__(self, manager: Manager):
        self.manager: Manager = manager
        self.model: Usr = Usr
    async def get_by_id(self, id: int) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Usr]:
        query = self.model.select()
        return list(await self.manager.fetchall(query))
    async def get_by_login(self, login: str) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str) -> Usr:
        return await self.manager.create(self.model, login=login.strip().lower(), password=password, email=email.strip().lower(), avatar=None)
    async def update(self, usr: Union[int,Usr], **kwargs) -> bool:
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.update(**kwargs).where(self.model.id==usr_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, usr: Union[Usr, int]) -> bool:
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.delete().where(self.model.id == usr_id)
        return await self.manager.execute(query) > 0 # bool!
    
class SessionRepository:
    def __init__(self, manager: Manager):
        self.manager: Manager = manager
        self.model: Session = Session
    async def get_by_key(self, key: str) -> Optional[Session]:
        # Primary key of Session class has name "key", not the "id"
        return await self.manager.get_or_none(self.model, key=key)
    async def get_user_id_by_key(self, key: str) -> Optional[int]:
        session = await self.get_by_key(key)
        return session.user_id.id if session is not None else None
    async def getUsr(self, key: str) -> Optional[Usr]:
        session = await self.get_by_key(key)
        return session.user_id if session is not None else None
    async def get_all(self) -> List[Session]:
        query = self.model.select()
        return await list(self.manager.fetchall(query))
    async def get_expiredSessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at < date)
        return await list(self.manager.fetchall(query))
    async def get_activeSessions(self, date: date) -> List[Session]:
        query = self.model.select().where(self.model.expires_at >= date)
        return await list(self.manager.fetchall(query))
    async def get_byUsr(self, usr: Union[Usr, int]) -> List[Session]:
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.select().where(self.model.Usr_id == usr_id)
        return await self.manager.fetchall(query)
    async def create(self, key: str, usr: Union[int, Usr], created_at: date, expires_at: date) -> Session:
        return await self.manager.create(self.model, key=key, user_id=usr, created_at=created_at, expires_at=expires_at)
    async def delete(self, key: str) -> bool:
        query = self.model.delete().where(self.model.key == key)
        return await self.manager.execute(query) > 0 # bool!

class SecretRepository:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.model: Secret = Secret
    async def get_by_id(self, id: int) -> Optional[Secret]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Secret]:
        query = self.model.select()
        return await self.manager.fetchall(query)
    async def get_by_usr(self, usr: Union[int, Usr]) -> List[Secret]:
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.select().where(self.model.Usr_id == usr_id)
        return await self.manager.fetchall(query)
    async def create(self, usr: Union[int, Usr], text: str, image_path: Union[str, None]) -> Secret:
        return await self.manager.create(self.model, Usr_id=usr, text=text, image_path=image_path)
    async def update(self, secret: Union[int, Secret], **kwargs) -> bool:
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.update(**kwargs).where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, secret: Union[Secret, int]) -> bool:
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.delete().where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!