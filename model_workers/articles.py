from datetime import datetime
from typing import Optional, List

from data import db_session
from data.articles import Article
from data.users import User
from models.articles import ArticleInDB, CreateArticleData, \
    SearchByTitleModes, EditArticleData
from .comments import CommentModelWorker
from depends import errors


class ArticleModelWorker:
    @staticmethod
    def _pydantic_article_to_sql_article(article: ArticleInDB) -> Article:
        return Article(
            author_id=article.author_id,
            title=article.title,
            content=article.content,
            update_date=article.update_date if article.update_date is not None else datetime.now()
        )

    @staticmethod
    def _sql_article_to_pydantic_article(article: Article) -> ArticleInDB:
        return ArticleInDB(
            article_id=article.article_id,
            author_id=article.author_id,
            title=article.title,
            content=article.content,
            update_date=article.update_date
        )

    @staticmethod
    def get_article(article_id: int) -> ArticleInDB:
        with db_session.session_scope() as db_sess:
            article = db_sess.query(Article).get(article_id)
            if not article:
                raise errors.ArticleNotFoundError()
            return ArticleModelWorker._sql_article_to_pydantic_article(article)

    @staticmethod
    def get_articles(
            limit: int = 10,
            offset: int = 0,
            author_ids: Optional[List[int]] = None,
            title_search_string: Optional[str] = None,
            search_mode: SearchByTitleModes = SearchByTitleModes.STARTSWITH
    ) -> List[ArticleInDB]:
        with db_session.session_scope() as db_sess:
            articles = db_sess.query(Article)
            if author_ids is not None:
                articles = articles.filter(Article.author_id.in_(author_ids))
            if title_search_string is not None:
                if search_mode == SearchByTitleModes.EQUALS:
                    articles = articles.filter(Article.title == title_search_string)
                elif search_mode == SearchByTitleModes.EQUALS_CASE_INSENSITIVE:
                    articles = articles.filter(Article.title.like(title_search_string))
                elif search_mode == SearchByTitleModes.STARTSWITH:
                    articles = articles.filter(Article.title.startswith(title_search_string))
                elif search_mode == SearchByTitleModes.CONTAINS:
                    articles = articles.filter(Article.title.like(f"%{title_search_string}%"))
                else:
                    print(f"Unknown title search mode: {search_mode}")
            articles = articles.limit(limit).offset(offset)
            return [
                ArticleModelWorker._sql_article_to_pydantic_article(article) for article in articles
            ]

    @staticmethod
    def create_new_article(author_id: int, article_data: CreateArticleData) -> ArticleInDB:
        with db_session.session_scope() as db_sess:
            user = db_sess.query(User).get(author_id)
            if not user:
                raise errors.UserNotFoundError()
            db_article = ArticleInDB(
                article_id=-1,
                author_id=author_id,
                title=article_data.title,
                content=article_data.content
            )
            article: Article = ArticleModelWorker._pydantic_article_to_sql_article(db_article)
            db_sess.add(article)
            db_sess.commit()
            db_article.article_id = article.article_id
            db_article.update_date = article.update_date
            return db_article

    @staticmethod
    def edit_article(user_id: int, article_id: int, article_data: EditArticleData) -> ArticleInDB:
        with db_session.session_scope() as db_sess:
            article = db_sess.query(Article).get(article_id)
            if not article:
                raise errors.ArticleNotFoundError()
            if article.author_id != user_id:
                raise errors.ForbiddenToUserError()
            if article_data.title is not None:
                article.title = article_data.title
            if article_data.content is not None:
                article.content = article_data.content
            article.update_date = datetime.now()
            return ArticleModelWorker._sql_article_to_pydantic_article(article)

    @staticmethod
    def delete_article(user_id: int, article_id: int) -> None:
        with db_session.session_scope() as db_sess:
            ArticleModelWorker.delete_article_(user_id, article_id, db_sess)

    @staticmethod
    def delete_article_(user_id: int, article_id: int, db_sess) -> None:
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise errors.ArticleNotFoundError()
        if article.author_id != user_id:
            raise errors.ForbiddenToUserError()
        for comment in article.comments:
            CommentModelWorker.delete_comment_(comment.author_id, comment.comment_id, db_sess)
        db_sess.delete(article)
