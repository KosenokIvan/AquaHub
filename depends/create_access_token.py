from typing import Optional
from datetime import timedelta, datetime

from jose import jwt

import constants as cst
import jwt_key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_key.SECRET_KEY, algorithm=cst.ALGORITHM)
    return encoded_jwt
