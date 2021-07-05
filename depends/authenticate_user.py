from model_workers.users import UserModelWorker
from data import db_session
from models.users import UserInDB
from .password_hash import verify_password
from .errors import UserNotFoundError, IncorrectNicknameOrPasswordError


def authenticate_user(nickname: str, password: str) -> UserInDB:
    try:
        user: UserInDB = UserModelWorker.get_user_by_nickname(nickname)
    except UserNotFoundError as er:
        raise er
    if not verify_password(password, user.hashed_password):
        raise IncorrectNicknameOrPasswordError()
    return user
