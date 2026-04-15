from peewee_aio import Manager
from typing import Optional, List, Union
from datetime import date
from re import fullmatch
# own code
from src.entities import Usr, Session, Secret
from src.const import EMAIL_RE_PATTERN as EMAIL_RE_PATTERN
from src.exceptions import ValidationError

def invalid_fields_check(fields: list, allowed_fields: list):
    if fields - allowed_fields:
        raise ValueError("Invalid field(s) for update: " + ", ".join(fields - allowed_fields))
    

class UsrRepository:
    def __init__(self, manager: Manager):
        self.manager: Manager = manager
        self.model: Usr = Usr
        self.allowed_fields: tuple = tuple(Usr._meta.fields.keys() - 'id') # without id, because user cannot know his own id
    async def get_by_id(self, id: int) -> Optional[Usr]:
        return await self.manager.get_or_none(self.model, id=id)
    async def get_all(self) -> List[Usr]:
        query = self.model.select()
        return list(await self.manager.fetchall(query))
    async def get_by_login(self, login: str) -> Optional[Usr]:
        login = self.validation_login()
        return await self.manager.get_or_none(self.model, self.model.login == login.strip().lower())
    async def get_by_email(self, email: str) -> Optional[Usr]:
        email = self.validation_email()
        return await self.manager.get_or_none(self.model, self.model.email == email.strip().lower())
    async def create(self, login: str, password: str, email: str) -> Usr:
        login = self.validation_login()
        email = self.validation_email()
        password = self.validation_password()
        return await self.manager.create(self.model, login=login.strip().lower(), password=password, email=email.strip().lower(), avatar=None)
    async def update(self, usr: Union[int,Usr], **kwargs) -> bool:
        invalid_fields_check(kwargs.keys(), self.allowed_fields)
        if 'login' in kwargs:
            kwargs['login'] = self.validation_login(kwargs['login'])
        if 'email' in kwargs:
            kwargs['email'] = self.validation_email(kwargs['email'])
        
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.update(**kwargs).where(self.model.id==usr_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, usr: Union[Usr, int]) -> bool:
        usr_id = usr.id if isinstance(usr, Usr) else usr
        query = self.model.delete().where(self.model.id == usr_id)
        return await self.manager.execute(query) > 0 # bool!
    @staticmethod
    def validation_login(login: str) -> str:
        if not login:
            raise ValueError("Login cannot be empty")
        if not isinstance(login, str):
            raise ValidationError("Wrong login's type")
        if len(login) < 6 or len(login) > 64:
            raise ValidationError("Login's length error")
        return login.strip().lower()
    @staticmethod
    def validation_email(email: str) -> str:
        if not email:
            raise ValueError("Email cannot be empty")
        if not isinstance(email, str):
            raise ValidationError("Wrong email's type")
        if not fullmatch(EMAIL_RE_PATTERN, email):
            raise ValidationError("Email does not match the pattern")
        if len(email) > 256:
            raise ValidationError("Email cannot be longer than 256 symbols")
        return email.strip().lower()
    @staticmethod
    def validation_password(password: str) -> str:
        if not password:
            raise ValueError('Password cannot be empty')
        if not isinstance(password, str):
            raise ValidationError("Wrongs password's type")
        if len(password) < 8 or len(password) > 72:
            raise ValidationError("Password's length error")
        return password
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
        self.allowed_fields: list = Secret._meta.fields.keys()
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
        invalid_fields_check(kwargs.keys(), self.allowed_fields)
        if 'text' in kwargs and isinstance(kwargs['text'], str): kwargs['text'] = kwargs['text'].strip()
        if 'image_path' in kwargs and isinstance(kwargs['image_path'], str): kwargs['image_path'] = kwargs['image_path'].strip()
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.update(**kwargs).where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!
    async def delete(self, secret: Union[Secret, int]) -> bool:
        secret_id = secret if isinstance(secret, int) else secret.id
        query = self.model.delete().where(self.model.id == secret_id)
        return await self.manager.execute(query) > 0 # bool!