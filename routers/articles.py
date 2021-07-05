from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from model_workers.articles import ArticleModelWorker
from models.articles import ArticleOut, CreateArticleData, ArticleInDB, \
    SearchByTitleModes, EditArticleData
from models.users import UserInDB
from depends.get_current_user import get_current_user
from depends import errors

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", status_code=201, response_model=ArticleOut)
async def create_article(
        article_data: CreateArticleData,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        article: ArticleInDB = ArticleModelWorker.create_new_article(
            current_user.user_id, article_data
        )
    except errors.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return ArticleOut(
        article_id=article.article_id,
        author_id=article.author_id,
        title=article.title,
        content=article.content,
        update_date=article.update_date
    )


@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int):
    try:
        return ArticleModelWorker.get_article(article_id)
    except errors.ArticleNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )


@router.get("/", response_model=List[ArticleOut])
async def get_articles(
        limit: int = Query(10, gt=0, le=100),
        offset: int = Query(0, ge=0),
        author_ids: Optional[List[int]] = Query(None),
        title_search_string: Optional[str] = Query(None, min_length=3),
        title_search_mode: SearchByTitleModes = SearchByTitleModes.STARTSWITH
):
    articles = ArticleModelWorker.get_articles(
        limit,
        offset,
        author_ids,
        title_search_string,
        title_search_mode
    )
    return articles


@router.put("/{article_id}", response_model=ArticleOut)
async def edit_article(
        article_id: int,
        article_data: EditArticleData,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        article = ArticleModelWorker.edit_article(current_user.user_id, article_id, article_data)
    except errors.ArticleNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )
    except errors.ForbiddenToUserError:
        raise HTTPException(
            status_code=403,
            detail="You aren't author of this article"
        )
    return article


@router.delete("/{article_id}", response_model=None)
async def delete_article(
        article_id: int,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        ArticleModelWorker.delete_article(current_user.user_id, article_id)
    except errors.ArticleNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )
    except errors.ForbiddenToUserError:
        raise HTTPException(
            status_code=403,
            detail="You aren't author of this article"
        )
