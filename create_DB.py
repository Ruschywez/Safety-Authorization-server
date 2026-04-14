from peewee_aio import Manager
from src.const import DB_TABLES, DB_URL
import asyncio

async def create_tables(*tables):
    manager: Manager = Manager(DB_URL)
    for table in tables:
        manager.register(table)
    await manager.create_tables(*tables)
if __name__ == "__main__":
    asyncio.run(create_tables(*DB_TABLES))