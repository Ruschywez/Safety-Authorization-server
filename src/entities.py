from peewee import AutoField, CharField, TextField, ForeignKeyField, Model, Proxy, DateField



class BaseModel(Model):
    class Meta:
        database = Proxy()
class User(Model):
    id = AutoField(primary_key=True, column_name="id")
    login = CharField(max_length=64, unique=True)
    password = CharField(max_length=72)
    email = CharField(max_length=256, unique=True, null=True)
    avatar = CharField(max_length=256, null=True)
    class Meta:
        table_model="usr"
class Secret(Model):
    id = AutoField(primary_key=True, column_name="id")
    text = TextField(column_name="text")
    image_path = CharField(max_length=256, null=True, column_name="image_path")
    user_id = ForeignKeyField(User, backref="secrets", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    class Meta:
        table_name="secret"
class Session(Model):
    key = CharField(max_length=256, primary_key=True, column_name="id")
    user_id = ForeignKeyField(User, backref="sessions", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    created_at = DateField(column_name="created_at")
    expires_at = DateField(column_name="expires_at")
    class meta:
        table_name="session"