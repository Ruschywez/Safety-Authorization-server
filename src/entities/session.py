from peewee import Model, CharField, ForeignKeyField, DateField, Proxy
from user import User
session_db = Proxy()
class Session(Model):
    key = CharField(max_length=256, primary_key=True, column_name="id")
    user_id = ForeignKeyField(User, backref="sessions", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    created_at = DateField(column_name="created_at")
    expires_at = DateField(column_name="expires_at")
    class meta:
        database = session_db