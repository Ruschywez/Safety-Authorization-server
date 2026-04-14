from pydantic import BaseModel
from fastapi import Query
from typing import Optional
"""file for pydantic models
    Not all validation are here. Some of requests have own validation with Query class,
    because they are too small and simple for own class.
"""

class KeyRequest(BaseModel):
    session_key: str = Query(..., length=252)

class RegistrationRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)
    email: str = Query(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class LoginRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)

class ChangeProfileRequest(BaseModel):
    session_key: str = Query(..., length=256)
    login: Optional[str] = Query(None, min_length=6, max_length=64)
    password: Optional[str] = Query(None, min_length=8, max_length=72)
    email: Optional[str] = Query(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')