from src.db_connect import DataBase
from src.entities import Usr, Session, Secret
import asyncio

async def create_tables():
    database = DataBase(Usr, Session, Secret)
    await database.init()

if __name__ == "__main__":
    asyncio.run(create_tables())