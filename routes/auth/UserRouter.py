from datetime import date
from typing import List, Union
from fastapi import APIRouter, Depends, Query, status

from schemas.auth.UserSchema import (
    UserAccessToken,
    UserChangePassword,
    UserModeSelect,
    UserNormalized,
    UserPost,
    UserPost,
    UserUpdate,
    UsersResponse,
)

from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from services.auth.UserService import UserService

UserRouter = APIRouter(tags=["User"], prefix="/user")


@UserRouter.get(
    "",
    response_model=Union[List[UserModeSelect], UsersResponse],
    status_code=status.HTTP_200_OK,
)
async def get(
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
    active: bool = None,
    offset: int = 0,
    limit: int = 150,
    search: str = None,
    mode_select: bool = False,
    comission_parameters: bool = None,
) -> Union[List[UserModeSelect], UsersResponse]:
    if await AuthService.verify_permission(0, user):
        return userService.get(
            active=active,
            offset=offset,
            limit=limit,
            search=search,
            mode_select=mode_select,
            comission_parameters=comission_parameters,
        )
    else:
        ErrorsService().unauthorized()


@UserRouter.get(
    "/{id}",
    response_model=UserNormalized,
    status_code=status.HTTP_200_OK,
)
async def get_id(
    id: int,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserNormalized:
    if await AuthService.verify_permission(0, user):
        return userService.get_id(id)
    else:
        ErrorsService().unauthorized()


@UserRouter.post("", response_model=UserNormalized, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_form: UserPost,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserNormalized:
    if await AuthService.verify_permission(0, user):
        return userService.create(user_form)

    else:
        ErrorsService().unauthorized()


@UserRouter.put(
    "/change_password_temp",
    response_model=UserAccessToken,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    userChangePassword: UserChangePassword,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_change_password_temp),
) -> UserAccessToken:
    return await userService.change_password(
        id=user.id, password=userChangePassword.password
    )


@UserRouter.put(
    "/change_password", response_model=UserAccessToken, status_code=status.HTTP_200_OK
)
async def change_password(
    userChangePassword: UserChangePassword,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserAccessToken:
    return await userService.change_password(
        id=user.id, password=userChangePassword.password
    )


@UserRouter.put(
    "/{id}/restore_password",
    response_model=UserNormalized,
    status_code=status.HTTP_200_OK,
)
async def restore_password(
    id: int,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserNormalized:
    if await AuthService.verify_permission(0, user):
        return userService.reset_password(id=id)

    else:
        ErrorsService().unauthorized()


@UserRouter.put("/{id}", response_model=UserNormalized, status_code=status.HTTP_200_OK)
async def update_user(
    id: int,
    user_update: UserUpdate,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserNormalized:
    if await AuthService.verify_permission(0, user):
        return userService.update(user_update=user_update, id=id)

    else:
        ErrorsService().unauthorized()


@UserRouter.put(
    "/{id}/{state}", response_model=UserNormalized, status_code=status.HTTP_200_OK
)
async def on_off_user(
    id: int,
    state: bool,
    userService: UserService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserNormalized:
    if await AuthService.verify_permission(0, user):
        return userService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
