import fastapi
from fastapi import Depends, Form, HTTPException, status, Query
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

# I've build that, hell yeah
from src.services import UsrService, SessionService, SecretService
from src.imageManager import ImageManager
from src.encryption import CryptManager
from src.db_connect import DataBase
from src.entities import Usr, Session, Secret
from src.repositories import UsrRepository, SessionRepository, SecretRepository

# public voids


database = DataBase(Usr, Session, Secret)
manager = database.manager
usr_repository = UsrRepository(manager)
session_repository = SessionRepository(manager)
secret_repository = SecretRepository(manager)

crypt_manager = CryptManager()
image_manager = ImageManager(crypt_manager)
session_service = SessionService(session_repository, usr_repository, crypt_manager)
usr_service= UsrService(usr_repository, session_service, crypt_manager, image_manager)
secret_service = SecretService(secret_repository, session_service, image_manager, crypt_manager)
app = fastapi.FastAPI()

class KeyRequest(BaseModel):
    session_key: str = Query(..., length=252)

@app.get("/ping")
async def ping() -> bool:
    return True
@app.get("/check_key")
async def check_key(request: KeyRequest = Depends()) -> bool:
    try:
        return await session_service.is_session_key_valid(request.session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Registration"""
class RegistrationRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)
    email: str = Query(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
@app.post("/registration")
async def registration(request: RegistrationRequest = Depends()) -> bool:
    try:
        await usr_service.register(login=request.login, password=request.password, email=request.email)
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Login"""
class LoginRequest(BaseModel):
    login: str = Query(..., min_length=6, max_length=64)
    password: str = Query(..., min_length=8, max_length=72)
@app.post("/login")
async def login(request: LoginRequest = Depends()) -> str:
    try:
        return await session_service.authentication(login=request.login, password=request.password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Logout"""
@app.delete("/logout")
async def logout(session_key: KeyRequest = Depends()) -> bool:
    # key will be deleted from sessions
    try:
        return await session_service.logout(session_key=session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Change profile data"""
@app.get("/profile")
async def get_profile(session_key: KeyRequest = Depends()) -> dict:
    try:
        profile = await usr_service.get_user_info(key=session_key)
        if profile is None:
            raise HTTPException(status_code=404, detail="User not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
class ChangeProfileRequest(BaseModel):
    session_key: str = Query(..., length=256)
    login: Optional[str] = Query(None, min_length=6, max_length=64)
    password: Optional[str] = Query(None, min_length=8, max_length=72)
    email: Optional[str] = Query(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
@app.patch("/profile")
async def change_profile(request: ChangeProfileRequest = Depends()) -> bool:
    try:
        return await usr_service.update_profile(key=request.session_key, **request.dict(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.delete("/profile")
async def delete_profile(session_key: KeyRequest = Depends()) -> bool:
    try:
        return await usr_service.delete_user(key=session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Avatar"""
@app.post("/profile/set_avatar")
async def set_avatar(session_key: KeyRequest, avatar: bytes) -> bool:
    try:
        return await usr_service.set_avatar(key=session_key, avatar=avatar)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.delete("/profile/avatar")
async def delete_avatar(session_key: KeyRequest = Depends()) -> bool:
    try:
        return await usr_service.delete_avatar(key=session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""Secrets"""
@app.get("/secrets")
async def get_secrets(session_key: KeyRequest = Depends()) -> List[dict]:
    try:
        return await secret_service.get_user_secrets(key=session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/secrets/image")
async def get_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bytes:
    try:
        image = await secret_service.get_secret_image(key=session_key, secret_id=secret_id)
        if image is None:
            raise HTTPException(status_code=404, detail="Secret or image not found")
        return image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.post("/secrets")
async def create_secret(session_key: KeyRequest = Depends(), text: str = Query(..., min_length=1, max_length=1000), image: Optional[bytes] = None) -> dict:
    try:
        return await secret_service.create_secret(key=session_key, text=text, image=image)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.patch("/secrets")
async def update_secret_text(session_key: str = Query(..., length=256), secret_id: int = Query(..., ge=1), text: str = Query(..., min_length=1, max_length=1000)) -> bool:
    try:
        return await secret_service.update_secret(key=session_key, secret_id=secret_id, text=text, image=None)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.patch("/secrets/image")
async def update_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1), image: bytes = Form(...)) -> bool:
    try:
        return await secret_service.set_secret_image(key=session_key, secret_id=secret_id, image=image)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.delete("/secrets")
async def delete_secret(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bool:
    try:
        return await secret_service.delete_secret(key=session_key, secret_id=secret_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.delete("/secrets/image")
async def delete_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bool:
    try:
        return await secret_service.delete_secret_image(key=session_key, secret_id=secret_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))