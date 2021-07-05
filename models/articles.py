from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field

import constants as cst


class SearchByTitleModes(str, Enum):
    CONTAINS = "in"
    STARTSWITH = "start"
    EQUALS = "equ"
    EQUALS_CASE_INSENSITIVE = "equ_ci"


class Article(BaseModel):
    author_id: int
    title: str = Field(..., max_length=cst.ARTICLE_TITLE_MAX_LENGTH)
    content: Optional[str] = Field(None, max_length=cst.ARTICLE_CONTENT_MAX_LENGTH)


class ArticleInDB(Article):
    article_id: int
    update_date: Optional[datetime]


class ArticleOut(ArticleInDB):
    pass


class CreateArticleData(BaseModel):
    title: str = Field(..., max_length=cst.ARTICLE_TITLE_MAX_LENGTH)
    content: Optional[str] = Field(None, max_length=cst.ARTICLE_CONTENT_MAX_LENGTH)


class EditArticleData(BaseModel):
    title: Optional[str] = Field(None, max_length=cst.ARTICLE_TITLE_MAX_LENGTH)
    content: Optional[str] = Field(None, max_length=cst.ARTICLE_CONTENT_MAX_LENGTH)
