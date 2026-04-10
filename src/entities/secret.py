from peewee import AutoField, CharField, TextField, ForeignKeyField, Model, Proxy
from user import User
secret_db = Proxy()
class Secret(Model):
    id = AutoField(primary_key=True, column_name="id")
    text = TextField(column_name="text")
    image_path = CharField(max_length=256, null=True, column_name="image_path")
    user_id = ForeignKeyField(User, backref="secrets", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    class Meta:
        database = secret_db