from datetime import datetime
import sqlalchemy as sq
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
import constants as cst


class Article(SqlAlchemyBase):
    __tablename__ = "articles"
    article_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    title = sq.Column(sq.String(256), nullable=False)
    author_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"), nullable=False)
    content = sq.Column(sq.String(cst.ARTICLE_CONTENT_MAX_LENGTH))
    update_date = sq.Column(sq.DateTime, default=datetime.now, nullable=False)
    author = relationship("User", back_populates="articles")
    comments = relationship("Comment", back_populates="article")
