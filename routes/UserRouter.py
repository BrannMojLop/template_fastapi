from typing import List
from fastapi import APIRouter, Depends, status
from models.User import TypeUser

from schemas.UserSchema import (
    UserBase,
    UserChangePassword,
    UserPost,
    UserResponse,
    UserUpdate,
)
from services.AuthService import AuthService
from services.ErrorsService import ErrorsService
from services.UserService import UserService

UserRouter = APIRouter(tags=["User"], prefix="/user")


@UserRouter.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_users(
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
    offset: int = 0,
    limit: int = 150,
    type: TypeUser = None,
) -> UserResponse:
    if await AuthService.verify_permission(0, user):
        return userService.get(offset=offset, limit=limit, type=type)
    else:
        ErrorsService().unauthorized()


@UserRouter.get(
    "/{id}",
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    id: int,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserBase:
    if await AuthService.verify_permission(0, user):
        return userService.get_id(id)
    else:
        ErrorsService().unauthorized()


@UserRouter.post("", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_form: UserPost,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserBase:
    if await AuthService.verify_permission(0, user):
        return userService.create(user_form)

    else:
        ErrorsService().unauthorized()


@UserRouter.put(
    "/change_password", response_model=UserBase, status_code=status.HTTP_200_OK
)
async def change_password(
    userChangePassword: UserChangePassword,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_change_password),
) -> UserBase:
    return userService.change_password(id=user.id, password=userChangePassword.password)


@UserRouter.put("/{id}", response_model=UserBase, status_code=status.HTTP_200_OK)
async def update_user(
    id: int,
    user_update: UserUpdate,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserBase:
    if await AuthService.verify_permission(0, user):
        return userService.update(user_update=user_update, id=id)

    else:
        ErrorsService().unauthorized()


@UserRouter.put(
    "/{id}/restore_password",
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
)
async def restore_password(
    id: int,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserBase:
    if await AuthService.verify_permission(0, user):
        return userService.reset_password(id=id)

    else:
        ErrorsService().unauthorized()


@UserRouter.put(
    "/{id}/{state}", response_model=UserBase, status_code=status.HTTP_200_OK
)
async def on_off_user(
    id: int,
    state: bool,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserBase:
    if await AuthService.verify_permission(0, user):
        return userService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
