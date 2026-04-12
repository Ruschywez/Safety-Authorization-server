import asyncio
from pathlib import Path
from src.db_connect import DataBase
from src.entities import Usr, Secret, Session
from src.repositories import UsrRepository, SessionRepository, SecretRepository
from peewee_aio import Manager


async def main():
    database = DataBase(Usr, Session, Secret)
    await database.init()
    manager = database.manager

    user_repository = UsrRepository(manager, Usr)
    session_repository = SessionRepository(manager, Session)
    secret_repository = SecretRepository(manager, Secret)

    #await user_repository.create(login="user12345", password="password12345", email="email12@gmail.com")
    users = await user_repository.get_all()
    print(users[0].login)
    user = await user_repository.get_by_id(1)
    print(user.login)


if __name__ == "__main__":
    asyncio.run(main())