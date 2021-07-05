from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException

from depends.get_current_user import get_current_user
from depends import errors

from models.users import UserOut, UserRegistrationData, \
    UserInDB, UserEditData, UserMeOut, SearchByNicknameMode
from model_workers.users import UserModelWorker

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", status_code=201, response_model=UserOut)
async def register(user_data: UserRegistrationData):
    try:
        db_user: UserInDB = UserModelWorker.create_new_user(user_data)
    except errors.NicknameAlreadyUseError:
        raise HTTPException(
            status_code=400,
            detail="Nickname already use"
        )
    except errors.EmailAlreadyUseError:
        raise HTTPException(
            status_code=400,
            detail="Email already use"
        )
    return UserOut(
        user_id=db_user.user_id,
        nickname=db_user.nickname,
        description=db_user.description,
        registration_date=db_user.registration_date
    )


@router.get("/", response_model=List[UserOut])
async def get_all_users(
        limit: int = Query(10, gt=0, le=100),
        offset: int = Query(0, ge=0),
        nickname_search_string: Optional[str] = Query(None, min_length=3),
        nickname_search_mode: SearchByNicknameMode = Query(SearchByNicknameMode.STARTSWITH)
):
    return [UserOut(
        user_id=user.user_id,
        nickname=user.nickname,
        description=user.description,
        registration_date=user.registration_date
    ) for user in UserModelWorker.get_users(
        limit,
        offset,
        nickname_search_string,
        nickname_search_mode
    )]


@router.get("/me", response_model=UserMeOut)
async def read_users_me(current_user: UserMeOut = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
        user_id: int
):
    try:
        user = UserModelWorker.get_user(user_id)
    except errors.UserNotFoundError:
        raise HTTPException(
            status_code=404, detail="User not found"
        )
    return UserOut(
        user_id=user.user_id,
        nickname=user.nickname,
        description=user.description,
        registration_date=user.registration_date
    )


@router.put("/", response_model=UserOut)
async def edit_user(
        user_data: UserEditData,
        current_user: UserOut = Depends(get_current_user)
):
    try:
        user: UserOut = UserModelWorker.edit_user(current_user.user_id, user_data)
    except errors.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    except errors.EmailAlreadyUseError:
        raise HTTPException(
            status_code=400,
            detail="Email already use"
        )
    return user


@router.delete("/", response_model=None)
async def delete_user(current_user: UserOut = Depends(get_current_user)):
    try:
        UserModelWorker.delete_user(current_user.user_id)
    except errors.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
