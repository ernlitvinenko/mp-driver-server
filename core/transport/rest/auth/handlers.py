import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from core.config import Config
from core.errors.auth.errors import profile_not_founded, incorrect_phone_number
from core.storage import profile_storage

router = APIRouter(prefix="/auth")


class Token(BaseModel):
    access_token: str
    token_type: str


class PhoneNumberRequest(BaseModel):
    phoneNumber: str


class TokenRequest(BaseModel):
    token: str


@router.post("/phone")
async def get_authorization_code(req: PhoneNumberRequest):
    for char in req.phoneNumber:
        if not char.isdigit():
            incorrect_phone_number()
        if not 10 <= len(req.phoneNumber) <= 12:
            incorrect_phone_number()

    p = profile_storage.get_profile_by_phone("".join(char for char in req.phoneNumber if char.isdigit()))
    if not p:
        profile_not_founded()
    return {"code": profile_storage.generate_profile_auth_code(p.id, p.phone_number)}


@router.post("/phone/code")
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    p = profile_storage.get_profile_by_phone(''.join(char for char in form_data.username if char.isdigit()))
    if not p:
        profile_not_founded()

    check = profile_storage.check_profile_code(p.id, form_data.password)
    if not check:
        raise HTTPException(status_code=403, detail="Incorrect code")

    token = jwt.encode({"profile_id": p.id, "exp": time.time() + 60 * 60 * 24}, algorithm="HS256", key=Config.secret)
    return Token(access_token=token, token_type="bearer")


@router.get("/token")
async def test_access_token(token: str = Header(alias="Authorization")):
    try:
        jwt.decode(token.split(" ")[1], Config.secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
    return {}
