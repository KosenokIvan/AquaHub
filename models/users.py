from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field

import constants as cst

EMAIL_REGEX = r"^\w+@\w+\.\w+$"
NICKNAME_REGEX = r"^\w+$"


class SearchByNicknameMode(str, Enum):
    STARTSWITH = "start"
    EQUALS = "equ"
    EQUALS_CASE_INSENSITIVE = "equ_ci"


class User(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=64, regex=NICKNAME_REGEX)
    description: Optional[str] = Field(None, max_length=cst.DESCRIPTION_MAX_LENGTH)


class UserWithId(User):
    user_id: int


class UserWithRegistrationDate(User):
    registration_date: Optional[datetime]


class UserOut(UserWithId, UserWithRegistrationDate):
    pass


class UserMeOut(UserOut):
    email: str = Field(..., max_length=64, regex=EMAIL_REGEX)


class UserInDB(UserWithId, UserWithRegistrationDate):
    hashed_password: str
    email: str = Field(..., max_length=64, regex=EMAIL_REGEX)


class UserRegistrationData(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=64, regex=NICKNAME_REGEX)
    description: Optional[str] = Field(None, max_length=cst.DESCRIPTION_MAX_LENGTH)
    email: str = Field(..., max_length=64, regex=EMAIL_REGEX)
    password: str = Field(
        ...,
        min_length=cst.PASSWORD_MIN_LENGTH,
        max_length=cst.PASSWORD_MAX_LENGTH
    )


class UserEditData(BaseModel):
    description: Optional[str] = Field(None, max_length=cst.DESCRIPTION_MAX_LENGTH)
    email: Optional[str] = Field(None, max_length=64, regex=EMAIL_REGEX)
    password: Optional[str] = Field(
        None,
        min_length=cst.PASSWORD_MIN_LENGTH,
        max_length=cst.PASSWORD_MAX_LENGTH
    )


class UserLoginData(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=64, regex=NICKNAME_REGEX)
    password: str = Field(..., max_length=cst.PASSWORD_MAX_LENGTH)
