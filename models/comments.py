from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import constants as cst


class Comment(BaseModel):
    article_id: int
    author_id: int
    content: Optional[str] = Field(None, max_length=cst.COMMENT_CONTENT_MAX_LENGTH)


class CommentInDB(Comment):
    comment_id: int
    update_date: Optional[datetime]


class CommentOut(CommentInDB):
    pass


class CreateCommentData(BaseModel):
    article_id: int
    content: Optional[str] = Field(None, max_length=cst.COMMENT_CONTENT_MAX_LENGTH)


class EditCommentData(BaseModel):
    content: Optional[str] = Field(None, max_length=cst.COMMENT_CONTENT_MAX_LENGTH)
