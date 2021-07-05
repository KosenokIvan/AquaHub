from datetime import timedelta
from fastapi import HTTPException
from .create_access_token import create_access_token
from .authenticate_user import authenticate_user
from models.users import UserInDB
from .errors import UserNotFoundError, IncorrectNicknameOrPasswordError
import constants as cst


def get_token(nickname, password):
    bad_login_exception = HTTPException(
            status_code=401,
            detail="Incorrect nickname or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        user: UserInDB = authenticate_user(nickname, password)
    except UserNotFoundError:
        raise bad_login_exception
    except IncorrectNicknameOrPasswordError:
        raise bad_login_exception
    access_token_expires = timedelta(minutes=cst.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.nickname}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
