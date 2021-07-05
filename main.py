from datetime import timedelta

from fastapi import FastAPI, Request, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm

from depends.get_token import get_token

from data import db_session

from models.tokens import Token
from models.users import UserLoginData

from routers import users, articles, comments

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with **users**"
    },
    {
        "name": "articles",
        "description": "Operations with **articles**"
    },
    {
        "name": "comments",
        "description": "Operations with **comments**"
    },
    {
        "name": "authorization",
        "description": "Operations for getting **tokens**"
    }
]

app = FastAPI(
    openapi_tags=tags_metadata,
    title="AquaHub project",
    description="Test project on FastApi",
    version="0.0.2"
)

app.include_router(users.router)
app.include_router(articles.router)
app.include_router(comments.router)

db_session.global_init("db/aquahub.db")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = db_session.create_session()
        response = await call_next(request)
    finally:
        pass
    return response


@app.post("/token", response_model=Token, tags=["authorization"])
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return get_token(form_data.username, form_data.password)


@app.post("/login", response_model=Token, tags=["authorization"])
async def login_for_access_token(user_data: UserLoginData):
    return get_token(user_data.nickname, user_data.password)
