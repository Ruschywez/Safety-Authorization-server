from pydantic import BaseModel
from fastapi import Query
from typing import Optional
from src.const import EMAIL_RE_PATTERN
"""file for pydantic models
    Not all validation are here. Some of requests have own validation with Query class,
    because they are too small and simple for own class.
"""

class KeyRequest(BaseModel):
    session_key: str = Query(..., min_length=64, max_length=256)

class RegistrationRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)
    email: str = Query(..., pattern=EMAIL_RE_PATTERN)

class LoginRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)

class ChangeProfileRequest(BaseModel):
    session_key: str = Query(..., length=256)
    login: Optional[str] = Query(None, min_length=6, max_length=64)
    password: Optional[str] = Query(None, min_length=8, max_length=72)
    email: Optional[str] = Query(None, pattern=EMAIL_RE_PATTERN)