from datetime import datetime
import sqlalchemy as sq
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
import constants as cst


class Comment(SqlAlchemyBase):
    __tablename__ = "comments"
    comment_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    article_id = sq.Column(sq.Integer, sq.ForeignKey("articles.article_id"), nullable=False)
    author_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"), nullable=False)
    content = sq.Column(sq.String(cst.COMMENT_CONTENT_MAX_LENGTH), nullable=False)
    update_date = sq.Column(sq.DateTime, default=datetime.now)
    article = relationship("Article", back_populates="comments")
    author = relationship("User", back_populates="comments")
