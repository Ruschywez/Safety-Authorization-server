from fastapi import APIRouter, Depends, Form, HTTPException, status, Query
from typing import List, Optional
# I've build that, hell yeah
# Pydantic models I put in Models.py
from src.models import KeyRequest, RegistrationRequest, LoginRequest, ChangeProfileRequest
from src.container import get_secret_service, get_session_service, get_usr_service
from src.exceptions import *
#services from container
usr_service = get_usr_service()
session_service = get_session_service()
secret_service = get_secret_service()

# main router
router = APIRouter()

# simple ping
@router.get("/ping")
async def ping() -> bool:
    return True
"""
    Sessions' requests
    1) /login session creating
    2) /check_key session key validation
    3) /logout session deleting

    Non-deleted key's will still be valid, but they will be deleted after expiration time.
"""
@router.get("/check_key")
async def check_key(request: KeyRequest = Depends()) -> bool:
    """demonstration of the keys'
        This is main request of this project
        everything were created for this"""
    try:
        return await session_service.is_session_key_valid(request.session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest = Depends()) -> str:
    # key will be created and returned to user
    try:
        return await session_service.authentication(login=request.login, password=request.password)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except WrongPasswordError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/logout")
async def logout(session_key: KeyRequest = Depends()) -> bool:
    # key will be deleted from sessions
    try:
        return await session_service.logout(session_key=session_key)
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
    User's requests
    1) /registration creating new user
    2) /profile getting user info, changing profile and deleting profile
    3) /profile/avatar setting and deleting avatar
"""
@router.post("/registration")
async def registration(request: RegistrationRequest = Depends()) -> bool:
    try:
        await usr_service.register(login=request.login, password=request.password, email=request.email)
        return True
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/profile")
async def get_profile(session_key: KeyRequest = Depends()) -> dict:
    try:
        return await usr_service.get_user_info(key=session_key)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/profile")
async def change_profile(request: ChangeProfileRequest = Depends()) -> bool:
    try:
        return await usr_service.update_profile(key=request.session_key, **request.dict(exclude_unset=True))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/profile")
async def delete_profile(session_key: KeyRequest = Depends()) -> bool:
    try:
        return await usr_service.delete_user(key=session_key)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.get("/profile/avatar")
async def get_avatar(session_key: KeyRequest = Depends()) -> bytes:
    try:
        return await usr_service.get_avatar(key=session_key)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except AvatarNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/profile/avatar")
async def set_avatar(session_key: KeyRequest, avatar: bytes) -> bool:
    try:
        return await usr_service.set_avatar(key=session_key, avatar=avatar)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/profile/avatar")
async def delete_avatar(session_key: KeyRequest = Depends()) -> bool:
    try:
        return await usr_service.delete_avatar(key=session_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
    Secret's requests
    1) /secrets getting all user's secrets, creating new secret, changing secret's text and deleting secret
    2) /secrets/image getting secret's image, changing secret's image and deleting secret's image
"""
@router.get("/secrets")
async def get_secrets(session_key: KeyRequest = Depends()) -> List[dict]:
    try:
        return await secret_service.get_user_secrets(key=session_key)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secrets not found") 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/secrets")
async def create_secret(session_key: KeyRequest = Depends(), text: str = Query(..., min_length=1, max_length=1000), image: Optional[bytes] = None) -> dict:
    try:
        return await secret_service.create_secret(key=session_key, text=text, image=image)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/secrets")
async def update_secret_text(session_key: str = Query(..., length=256), secret_id: int = Query(..., ge=1), text: str = Query(..., min_length=1, max_length=1000)) -> bool:
    try:
        return await secret_service.update_secret(key=session_key, secret_id=secret_id, text=text, image=None)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/secrets")
async def delete_secret(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bool:
    try:
        return await secret_service.delete_secret(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/secrets/image")
async def get_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bytes:
    try:
        return await secret_service.get_secret_image(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except SecretImageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret has no image")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/secrets/image")
async def update_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1), image: bytes = Form(...)) -> bool:
    try:
        return await secret_service.set_secret_image(key=session_key, secret_id=secret_id, image=image)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/secrets/image")
async def delete_secret_image(session_key: KeyRequest = Depends(), secret_id: int = Query(..., ge=1)) -> bool:
    try:
        return await secret_service.remove_secret_image(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except SecretImageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))