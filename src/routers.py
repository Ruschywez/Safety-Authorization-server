from fastapi import APIRouter as _APIRouter, Depends as _Depends, Form as _Form, HTTPException as _HTTPException, status as _status, Query as _Query
from typing import List as _List, Optional as _Optional
# I've build that, hell yeah
# Pydantic models I put in Models.py
from src.models import KeyRequest as _KeyRequest, RegistrationRequest as _RegistrationRequest, LoginRequest as _LoginRequest, ChangeProfileRequest as _ChangeProfileRequest
from src.container import get_secret_service as _get_secret_service, get_session_service as _get_session_service, get_usr_service as _get_usr_service
from src.exceptions import *
#services from container
_usr_service = _get_usr_service()
_session_service = _get_session_service()
_secret_service = _get_secret_service()

# main router
router = _APIRouter()

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
async def check_key(request: _KeyRequest = _Depends()) -> bool:
    """demonstration of the keys'
        This is main request of this project
        everything were created for this"""
    try:
        return await _session_service.is_session_key_valid(request.session_key)
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login")
async def login(request: _LoginRequest = _Depends()) -> str:
    # key will be created and returned to user
    try:
        return await _session_service.authentication(login=request.login, password=request.password)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except WrongPasswordError:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/logout")
async def logout(session_key: _KeyRequest = _Depends()) -> bool:
    # key will be deleted from sessions
    try:
        return await _session_service.logout(session_key=session_key)
    except Exception as e: raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
    User's requests
    1) /registration creating new user
    2) /profile getting user info, changing profile and deleting profile
    3) /profile/avatar setting and deleting avatar
"""
@router.post("/registration")
async def registration(request: _RegistrationRequest = _Depends()) -> bool:
    try:
        await _usr_service.register(login=request.login, password=request.password, email=request.email)
        return True
    except ConflictError as e:
        raise _HTTPException(status_code=_status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/profile")
async def get_profile(session_key: _KeyRequest = _Depends()) -> dict:
    try:
        return await _usr_service.get_user_info(key=session_key)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/profile")
async def change_profile(request: _ChangeProfileRequest = _Depends()) -> bool:
    try:
        return await _usr_service.update_profile(key=request.session_key, **request.dict(exclude_unset=True))
    except ValidationError as e:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        raise _HTTPException(status_code=_status.HTTP_409_CONFLICT, detail=str(e))
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/profile")
async def delete_profile(session_key: _KeyRequest = _Depends()) -> bool:
    try:
        return await _usr_service.delete_user(key=session_key)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.get("/profile/avatar")
async def get_avatar(session_key: _KeyRequest = _Depends()) -> bytes:
    try:
        return await _usr_service.get_avatar(key=session_key)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except AvatarNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/profile/avatar")
async def set_avatar(session_key: _KeyRequest, avatar: bytes) -> bool:
    try:
        return await _usr_service.set_avatar(key=session_key, avatar=avatar)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/profile/avatar")
async def delete_avatar(session_key: _KeyRequest = _Depends()) -> bool:
    try:
        return await _usr_service.delete_avatar(key=session_key)
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
    Secret's requests
    1) /secrets getting all user's secrets, creating new secret, changing secret's text and deleting secret
    2) /secrets/image getting secret's image, changing secret's image and deleting secret's image
"""
@router.get("/secrets")
async def get_secrets(session_key: _KeyRequest = _Depends()) -> _List[dict]:
    try:
        return await _secret_service.get_user_secrets(key=session_key)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secrets not found") 
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/secrets")
async def create_secret(session_key: _KeyRequest = _Depends(), text: str = _Query(..., min_length=1, max_length=1000), image: _Optional[bytes] = None) -> dict:
    try:
        return await _secret_service.create_secret(key=session_key, text=text, image=image)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except ValidationError as e:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/secrets")
async def update_secret_text(session_key: str = _Query(..., length=256), secret_id: int = _Query(..., ge=1), text: str = _Query(..., min_length=1, max_length=1000)) -> bool:
    try:
        return await _secret_service.update_secret(key=session_key, secret_id=secret_id, text=text, image=None)
    except ValidationError as e:
        raise _HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/secrets")
async def delete_secret(session_key: _KeyRequest = _Depends(), secret_id: int = _Query(..., ge=1)) -> bool:
    try:
        return await _secret_service.delete_secret(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/secrets/image")
async def get_secret_image(session_key: _KeyRequest = _Depends(), secret_id: int = _Query(..., ge=1)) -> bytes:
    try:
        return await _secret_service.get_secret_image(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except SecretImageNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret has no image")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/secrets/image")
async def update_secret_image(session_key: _KeyRequest = _Depends(), secret_id: int = _Query(..., ge=1), image: bytes = _Form(...)) -> bool:
    try:
        return await _secret_service.set_secret_image(key=session_key, secret_id=secret_id, image=image)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/secrets/image")
async def delete_secret_image(session_key: _KeyRequest = _Depends(), secret_id: int = _Query(..., ge=1)) -> bool:
    try:
        return await _secret_service.remove_secret_image(key=session_key, secret_id=secret_id)
    except UserNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    except SecretNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except SecretImageNotFoundError:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Secret not found")
    except Exception as e:
        raise _HTTPException(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))