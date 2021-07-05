from datetime import datetime
from typing import List, Optional

from data import db_session
from data.users import User

from depends.password_hash import get_password_hash
from depends import errors

from models.users import UserInDB, UserRegistrationData, UserEditData, SearchByNicknameMode
from .articles import ArticleModelWorker
from .comments import CommentModelWorker


class UserModelWorker:
    @staticmethod
    def _sql_user_to_pydantic_user(user: User) -> UserInDB:
        return UserInDB(
            user_id=user.user_id,
            nickname=user.nickname,
            description=user.description,
            registration_date=user.registration_date,
            email=user.email,
            hashed_password=user.hashed_password
        )

    @staticmethod
    def _pydantic_user_to_sql_user(user: UserInDB) -> User:
        return User(
            nickname=user.nickname,
            description=user.description,
            email=user.email,
            hashed_password=user.hashed_password,
            registration_date=user.registration_date
            if user.registration_date is not None
            else datetime.now()
        )

    @staticmethod
    def get_user(user_id: int) -> UserInDB:
        with db_session.session_scope() as db_sess:
            user = db_sess.query(User).get(user_id)
            if not user:
                raise errors.UserNotFoundError()
            return UserModelWorker._sql_user_to_pydantic_user(user)

    @staticmethod
    def get_user_by_nickname(nickname: str) -> UserInDB:
        with db_session.session_scope() as db_sess:
            user = db_sess.query(User).filter(User.nickname == nickname).first()
            if not user:
                raise errors.UserNotFoundError()
            return UserModelWorker._sql_user_to_pydantic_user(user)

    @staticmethod
    def get_users(
            limit: int = 10,
            offset: int = 0,
            nickname_search_substring: Optional[str] = None,
            search_mode: SearchByNicknameMode = SearchByNicknameMode.STARTSWITH
    ) -> List[UserInDB]:
        with db_session.session_scope() as db_sess:
            users = db_sess.query(User)
            if nickname_search_substring is not None:
                if search_mode == SearchByNicknameMode.STARTSWITH:
                    users = users.filter(User.nickname.startswith(nickname_search_substring))
                elif search_mode == SearchByNicknameMode.EQUALS:
                    users = users.filter(User.nickname == nickname_search_substring)
                elif search_mode == SearchByNicknameMode.EQUALS_CASE_INSENSITIVE:
                    users = users.filter(User.nickname.like(nickname_search_substring))
                else:
                    print(f"Unknown nickname search mode: {search_mode}")
            users = users.limit(limit).offset(offset)
            return [UserModelWorker._sql_user_to_pydantic_user(user) for user in users]

    @staticmethod
    def create_new_user(user_data: UserRegistrationData) -> UserInDB:
        with db_session.session_scope() as db_sess:
            if db_sess.query(User).filter(User.nickname == user_data.nickname).first():
                raise errors.NicknameAlreadyUseError()
            if db_sess.query(User).filter(User.email == user_data.email).first():
                raise errors.EmailAlreadyUseError()
            db_user = UserInDB(
                user_id=-1,
                nickname=user_data.nickname,
                description=user_data.description,
                registration_date=None,
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password)
            )
            user: User = UserModelWorker._pydantic_user_to_sql_user(db_user)
            db_sess.add(user)
            db_sess.commit()
            db_user.user_id = user.user_id
            db_user.registration_date = user.registration_date
            return db_user

    @staticmethod
    def edit_user(user_id: int, user_data: UserEditData) -> UserInDB:
        with db_session.session_scope() as db_sess:
            user = db_sess.query(User).get(user_id)
            if not user:
                raise errors.UserNotFoundError()
            if user_data.email is not None:
                if db_sess.query(User).filter(
                        User.user_id != user_id,
                        User.email == user_data.email
                ).first():
                    raise errors.EmailAlreadyUseError()
                user.email = user_data.email
            if user_data.password is not None:
                user.hashed_password = get_password_hash(user_data.password)
            if user_data.description is not None:
                user.description = user_data.description
            result: UserInDB = UserModelWorker._sql_user_to_pydantic_user(user)
            return result

    @staticmethod
    def delete_user(user_id) -> None:
        with db_session.session_scope() as db_sess:
            UserModelWorker.delete_user_(user_id, db_sess)

    @staticmethod
    def delete_user_(user_id, db_sess) -> None:
        user = db_sess.query(User).get(user_id)
        if not user:
            raise errors.UserNotFoundError()
        for article in user.articles:
            ArticleModelWorker.delete_article_(article.author_id, article.article_id, db_sess)
        for comment in user.comments:
            CommentModelWorker.delete_comment_(comment.author_id, comment.comment_id, db_sess)
        db_sess.delete(user)
