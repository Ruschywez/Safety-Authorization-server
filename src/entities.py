from peewee import AnyField as _AutoField, CharField as _CharField, TextField as _TextField, ForeignKeyField as _ForeignKeyField, Model as _Model, DateField as _DateField

class Usr(_Model):
    id = _AutoField(primary_key=True, column_name="id")
    login = _CharField(max_length=64, unique=True)
    password = _CharField(max_length=72)
    email = _CharField(max_length=256, unique=True)
    avatar = _CharField(max_length=256, null=True, unique=True)
    class Meta:
        table_name="usr"
class Secret(_Model):
    id = _AutoField(primary_key=True, column_name="id")
    text = _TextField(column_name="text")
    image_path = _CharField(max_length=256, null=True, column_name="image_path", unique=True)
    user_id = _ForeignKeyField(Usr, backref="secrets", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    class Meta:
        table_name="secret"
class Session(_Model):
    key = _CharField(max_length=256, primary_key=True, column_name="id")
    user_id = _ForeignKeyField(Usr, backref="sessions", on_delete='CASCADE', on_update='CASCADE', column_name="user_id")
    created_at = _DateField(column_name="created_at")
    expires_at = _DateField(column_name="expires_at")
    class Meta:
        table_name="session"