from peewee_aio import Manager as _Manager
from typing import Optional as _Optional, List as _List, Union as _Union
from datetime import date as _date
from re import fullmatch as _fullmatch
# own code
from src.entities import Usr as _Usr, Session as _Session, Secret as _Secret
from src.const import EMAIL_RE_PATTERN as _EMAIL_RE_PATTERN
from src.exceptions import ValidationError as _ValidationError

class UsrRepository:
    def __init__(self, manager: _Manager):
        self.manager: _Manager = manager
        self.model: _Usr = _Usr
    async def get_by_id(self, id: int) -> _Optional[_Usr]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> _List[_Usr]:
        query = self.model.select()
        return list(await self.manager.fetchall(query))
    async def get_by_login(self, login: str) -> _Optional[_Usr]:
        if login is None: raise _ValidationError('Login cannot be None')
        if not isinstance(login, str): raise ValueError("Wrong login's type")
        if len(login) < 6 or len(login) > 64: raise _ValidationError("Login's length error")
        
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> _Optional[_Usr]:
        if email is None: raise _ValidationError('Email cannot be None')
        if not _fullmatch(_EMAIL_RE_PATTERN, email): _ValidationError("Email does not match the pattern")

        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str) -> _Usr:
        if login is None: raise _ValidationError('Login cannot be None')
        if len(login) < 6 or len(login) > 64: raise _ValidationError("Login's length error")
        if password is None: raise _ValidationError('Password cannot be None')
        if len(password) < 8 or len(password) > 72: raise _ValidationError("Password's length error")
        if email is None: raise _ValidationError('Email cannot be None')
        if not _fullmatch(_EMAIL_RE_PATTERN, email): _ValidationError("Email does not match the pattern")
        
        return await self.manager.create(self.model, login=login.strip().lower(), password=password, email=email.strip().lower(), avatar=None)
    async def update(self, usr: _Union[int,_Usr], **kwargs) -> bool:
        if kwargs.keys() - _Usr._meta.fields.keys(): raise ValueError(" Invalid field(s) for update: " + ", ".join(kwargs.keys() - _Usr._meta.fields.keys()))
        if 'id' in kwargs: raise ValueError("Cannot update primary key 'id'")
        if 'login' in kwargs and not isinstance(kwargs['login'], str): raise _ValidationError("Wrong login's type")
        if 'login' in kwargs and isinstance(kwargs['login'], str): kwargs['login'] = kwargs['login'].strip().lower()
        if 'email' in kwargs and not isinstance(kwargs['email'], str): raise _ValidationError("Wrong email's type")
        if 'email' in kwargs and not _fullmatch(_EMAIL_RE_PATTERN, kwargs['email']): _ValidationError("Email does not match the pattern")
        if 'email' in kwargs and isinstance(kwargs['email'], str): kwargs['email'] = kwargs['email'].strip().lower()
        
        usr_id = usr.id if isinstance(usr, _Usr) else usr
        query = self.model.update(**kwargs).where(self.model.id==usr_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, usr: _Union[_Usr, int]) -> bool:
        usr_id = usr.id if isinstance(usr, _Usr) else usr
        query = self.model.delete().where(self.model.id == usr_id)
        return await self.manager.execute(query) > 0 # bool!

class SessionRepository:
    def __init__(self, manager: _Manager):
        self.manager: _Manager = manager
        self.model: _Session = _Session
    async def get_by_key(self, key: str) -> _Optional[_Session]:
        # Primary key of _Session class has name "key", not the "id"
        return await self.manager.get_or_none(self.model, key=key)
    async def get_user_id_by_key(self, key: str) -> _Optional[int]:
        session = await self.get_by_key(key)
        return session.user_id.id if session is not None else None
    async def get_usr(self, key: str) -> _Optional[_Usr]:
        session = await self.get_by_key(key)
        return session.user_id if session is not None else None
    async def get_all(self) -> _List[_Session]:
        query = self.model.select()
        return await list(self.manager.fetchall(query))
    async def get_expired_sessions(self, _date: _date) -> _List[_Session]:
        query = self.model.select().where(self.model.expires_at < _date)
        return await list(self.manager.fetchall(query))
    async def get_active_sessions(self, _date: _date) -> _List[_Session]:
        query = self.model.select().where(self.model.expires_at >= _date)
        return await list(self.manager.fetchall(query))
    async def get_by_usr(self, usr: _Union[_Usr, int]) -> _List[_Session]:
        usr_id = usr.id if isinstance(usr, _Usr) else usr
        query = self.model.select().where(self.model.Usr_id == usr_id)
        return await self.manager.fetchall(query)
    async def create(self, key: str, usr: _Union[int, _Usr], created_at: _date, expires_at: _date) -> _Session:
        return await self.manager.create(self.model, key=key, user_id=usr, created_at=created_at, expires_at=expires_at)
    async def delete(self, key: str) -> bool:
        query = self.model.delete().where(self.model.key == key)
        return await self.manager.execute(query) > 0 # bool!

class SecretRepository:
    def __init__(self, manager: _Manager):
        self.manager = manager
        self.model: _Secret = _Secret
    async def get_by_id(self, id: int) -> _Optional[_Secret]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> _List[_Secret]:
        query = self.model.select()
        return await self.manager.fetchall(query)
    async def get_by_Usr(self, usr: _Union[int, _Usr]) -> _List[_Secret]:
        usr_id = usr.id if isinstance(usr, _Usr) else usr
        query = self.model.select().where(self.model.Usr_id == usr_id)
        return await self.manager.fetchall(query)
    async def create(self, usr: _Union[int, _Usr], text: str, image_path: _Union[str, None]) -> _Secret:
        return await self.manager.create(self.model, Usr_id=usr, text=text, image_path=image_path)
    async def update(self, secret: _Union[int, _Secret], **kwargs) -> bool:
        if kwargs.keys() - _Secret._meta.fields.keys(): raise ValueError("Invalid field(s) for update: " + ", ".join(kwargs.keys() - _Secret._meta.fields.keys()))
        if 'text' in kwargs and isinstance(kwargs['text'], str): kwargs['text'] = kwargs['text'].strip()
        if 'image_path' in kwargs and isinstance(kwargs['image_path'], str): kwargs['image_path'] = kwargs['image_path'].strip()
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.update(**kwargs).where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, secret: _Union[_Secret, int]) -> bool:
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.delete().where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!