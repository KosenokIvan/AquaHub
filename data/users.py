from datetime import datetime
import sqlalchemy as sq
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
import constants as cst


class User(SqlAlchemyBase):
    __tablename__ = "users"
    user_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    nickname = sq.Column(sq.String(64), unique=True, nullable=False, index=True)
    email = sq.Column(sq.String(64), unique=True, nullable=False)
    hashed_password = sq.Column(sq.String(512), nullable=False)
    registration_date = sq.Column(sq.DateTime, default=datetime.now)
    description = sq.Column(sq.String(cst.DESCRIPTION_MAX_LENGTH), nullable=True)
    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="author")
