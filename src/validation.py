import bcrypt
from re import fullmatch
from src.exceptions import ValidationError
from src.const import EMAIL_RE_PATTERN

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validation_login(login: str) -> str:
    if not login:
        raise ValueError("Login cannot be empty")
    if not isinstance(login, str):
        raise ValidationError("Wrong login's type")
    if len(login) < 6 or len(login) > 64:
        raise ValidationError("Login's length error")
    return login.strip().lower()
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
def validation_password(password: str) -> str:
    if not password:
        raise ValueError('Password cannot be empty')
    if not isinstance(password, str):
        raise ValidationError("Wrongs password's type")
    if len(password) < 8 or len(password) > 72:
        raise ValidationError("Password's length error")
    return password
def invalid_fields_check(fields: list, allowed_fields: list):
    if fields - allowed_fields:
        raise ValueError("Invalid field(s) for update: " + ", ".join(fields - allowed_fields))