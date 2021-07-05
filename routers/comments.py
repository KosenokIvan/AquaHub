from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from model_workers.comments import CommentModelWorker
from models.comments import CommentInDB, CommentOut, CreateCommentData, EditCommentData
from models.users import UserInDB
from depends.get_current_user import get_current_user
from depends import errors

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=CommentOut, status_code=201)
async def create_comment(
        comment_data: CreateCommentData,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        comment: CommentInDB = CommentModelWorker.create_comment(current_user.user_id, comment_data)
    except errors.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    except errors.ArticleNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )
    return comment


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(comment_id: int):
    try:
        comment: CommentInDB = CommentModelWorker.get_comment(comment_id)
    except errors.CommentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    return comment


@router.get("/", response_model=List[CommentOut])
async def get_comments(
        limit: int = Query(10, gt=0, le=100),
        offset: int = Query(0, ge=0),
        author_ids: Optional[List[int]] = Query(None),
        article_ids: Optional[List[int]] = Query(None)
):
    comments: List[CommentInDB] = CommentModelWorker.get_comments(
        limit,
        offset,
        author_ids,
        article_ids
    )
    return comments


@router.put("/{comment_id}", response_model=CommentOut)
async def edit_comment(
        comment_id: int,
        comment_data: EditCommentData,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        comment: CommentInDB = CommentModelWorker.edit_comment(
            current_user.user_id,
            comment_id,
            comment_data
        )
    except errors.CommentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    except errors.ForbiddenToUserError:
        raise HTTPException(
            status_code=403,
            detail="You aren't author of this comment"
        )
    return comment


@router.delete("/{comment_id}", response_model=None)
async def delete_comment(
        comment_id: int,
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        CommentModelWorker.delete_comment(current_user.user_id, comment_id)
    except errors.CommentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    except errors.ForbiddenToUserError:
        raise HTTPException(
            status_code=403,
            detail="You aren't author of this comment"
        )
