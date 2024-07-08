import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from core.config import Config
from core.model.profile.db import ProfileDB
from core.storage import profile_storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/phone")


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> ProfileDB:
    try:
        data = jwt.decode(token, algorithms="HS256", key=Config.secret)
    except jwt.exceptions.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail=str(err))

    except jwt.exceptions.InvalidSignatureError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return profile_storage.get_profile_by_id(data['profile_id'])
