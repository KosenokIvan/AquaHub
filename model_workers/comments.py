from datetime import datetime
from typing import Optional, List

from data.comments import Comment
from data.users import User
from data.articles import Article
from data import db_session
from depends import errors

from models.comments import CommentInDB, CreateCommentData, EditCommentData


class CommentModelWorker:
    @staticmethod
    def _sql_comment_to_pydantic_comment(comment: Comment) -> CommentInDB:
        return CommentInDB(
            comment_id=comment.comment_id,
            article_id=comment.article_id,
            author_id=comment.author_id,
            content=comment.content,
            update_date=comment.update_date
        )

    @staticmethod
    def _pydantic_comment_to_sql_comment(comment: CommentInDB) -> Comment:
        return Comment(
            article_id=comment.article_id,
            author_id=comment.author_id,
            content=comment.content,
            update_date=comment.update_date if comment.update_date is not None else datetime.now()
        )

    @staticmethod
    def create_comment(user_id: int, comment_data: CreateCommentData) -> CommentInDB:
        with db_session.session_scope() as db_sess:
            user = db_sess.query(User).get(user_id)
            if not user:
                raise errors.UserNotFoundError()
            article = db_sess.query(Article).get(comment_data.article_id)
            if not article:
                raise errors.ArticleNotFoundError()
            db_comment: CommentInDB = CommentInDB(
                comment_id=-1,
                article_id=comment_data.article_id,
                author_id=user_id,
                content=comment_data.content
            )
            comment = CommentModelWorker._pydantic_comment_to_sql_comment(db_comment)
            db_sess.add(comment)
            db_sess.commit()
            db_comment.comment_id = comment.comment_id
            db_comment.update_date = comment.update_date
            return db_comment

    @staticmethod
    def get_comment(comment_id: int) -> CommentInDB:
        with db_session.session_scope() as db_sess:
            comment = db_sess.query(Comment).get(comment_id)
            if not comment:
                raise errors.CommentNotFoundError()
            return CommentModelWorker._sql_comment_to_pydantic_comment(comment)

    @staticmethod
    def get_comments(
            limit: int = 10,
            offset: int = 0,
            author_ids: Optional[List[int]] = None,
            article_ids: Optional[List[int]] = None
    ) -> List[CommentInDB]:
        with db_session.session_scope() as db_sess:
            comments = db_sess.query(Comment)
            if author_ids is not None:
                comments = comments.filter(Comment.author_id.in_(author_ids))
            if article_ids is not None:
                comments = comments.filter(Comment.article_id.in_(article_ids))
            comments = comments.limit(limit).offset(offset)
            return [
                CommentModelWorker._sql_comment_to_pydantic_comment(comment) for comment in comments
            ]

    @staticmethod
    def edit_comment(user_id: int, comment_id: int, comment_data: EditCommentData) -> CommentInDB:
        with db_session.session_scope() as db_sess:
            comment = db_sess.query(Comment).get(comment_id)
            if not comment:
                raise errors.CommentNotFoundError()
            if comment.author_id != user_id:
                raise errors.ForbiddenToUserError()
            if comment_data.content is not None:
                comment.content = comment_data.content
            comment.update_date = datetime.now()
            return CommentModelWorker._sql_comment_to_pydantic_comment(comment)

    @staticmethod
    def delete_comment(user_id: int, comment_id: int) -> None:
        with db_session.session_scope() as db_sess:
            CommentModelWorker.delete_comment_(user_id, comment_id, db_sess)

    @staticmethod
    def delete_comment_(user_id: int, comment_id: int, db_sess) -> None:
        comment = db_sess.query(Comment).get(comment_id)
        if not comment:
            raise errors.CommentNotFoundError()
        if comment.author_id != user_id:
            raise errors.ForbiddenToUserError()
        db_sess.delete(comment)
