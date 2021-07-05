from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from .oauth2_scheme import oauth2_scheme
from data import db_session

from data.users import User

from models.users import UserOut, UserInDB
from models.tokens import TokenData

from model_workers.users import UserModelWorker

from depends import errors

import constants as cst
import jwt_key


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, jwt_key.SECRET_KEY, algorithms=[cst.ALGORITHM])
        nickname: str = payload.get("sub")
        if nickname is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    try:
        user = UserModelWorker.get_user_by_nickname(nickname)
    except errors.UserNotFoundError:
        raise credentials_exception
    return user
