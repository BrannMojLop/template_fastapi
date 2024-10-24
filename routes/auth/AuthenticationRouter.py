from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from config.Database import get_db_connection
from models.auth.User import User
from schemas.auth.UserSchema import (
    UserAccessToken,
    UserPostLogin,
)
from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from utils.records_validate import RecordsValiate

AuthenticationRouter = APIRouter(include_in_schema=False)


@AuthenticationRouter.post(
    "/api/login",
    response_model=UserAccessToken,
    status_code=status.HTTP_200_OK,
)
async def user_login(
    user_login: UserPostLogin,
    db: Session = Depends(get_db_connection),
) -> UserAccessToken:
    recordsValiate = RecordsValiate(db=db)
    user = recordsValiate.user(
        email=user_login.user, phone=user_login.user, username=user_login.user
    )

    userService = AuthService(**user.__dict__)
    if userService.verify_password(user_login.password):
        access_token = await userService.create_access_token()
        return access_token
    else:
        ErrorsService().credentials()


@AuthenticationRouter.post(
    "/api/token",
    response_model=UserAccessToken,
    status_code=status.HTTP_200_OK,
)
async def login_swagger(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_connection),
) -> UserAccessToken:
    recordsValiate = RecordsValiate(db=db)
    user = recordsValiate.user(email=username, phone=username, username=username)

    if user:
        userService = AuthService(**user.__dict__)
        if userService.verify_password(password):
            access_token = await userService.create_access_token()
            return access_token
        else:
            ErrorsService().credentials()
    else:
        ErrorsService().credentials()
