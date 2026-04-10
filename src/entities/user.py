from peewee import Model, AutoField, CharField, Proxy
user_db = Proxy()
class User(Model):
    id = AutoField(primary_key=True, column_name="id")
    login = CharField(max_length=64, unique=True)
    password = CharField(max_length=72)
    email = CharField(max_length=256, unique=True, null=True)
    avatar = CharField(max_length=256, null=True)
    class Meta:
        database = user_db