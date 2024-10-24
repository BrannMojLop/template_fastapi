from typing import List, Union
from fastapi import APIRouter, Depends, status
from schemas.auth.AppSchema import (
    AppBase,
    AppDetails,
    AppPost,
    AppsResponse,
)
from services.auth.AppService import AppService

from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService


AppRouter = APIRouter(tags=["App"], prefix="/app")


@AppRouter.get(
    "",
    response_model=Union[AppsResponse, List[AppDetails]],
    status_code=status.HTTP_200_OK,
)
async def get_apps(
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
    offset: int = 0,
    limit: int = 150,
    active: bool = None,
    user_id: int = None,
    views: bool = False,
) -> Union[AppsResponse, List[AppDetails]]:
    if await AuthService.verify_permission(0, user):
        return appService.get(
            offset=offset, limit=limit, active=active, user_id=user_id, views=views
        )
    else:
        ErrorsService().unauthorized()


@AppRouter.get(
    "/{id}",
    response_model=Union[AppBase, AppDetails],
    status_code=status.HTTP_200_OK,
)
async def get_app(
    id: int,
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
    views: bool = False,
) -> Union[AppBase, AppDetails]:
    if await AuthService.verify_permission(0, user):
        return appService.get_id(id=id, views=views)
    else:
        ErrorsService().unauthorized()


@AppRouter.get(
    "/user/available/{user_id}",
    response_model=AppsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_apps_available(
    user_id: int,
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> AppsResponse:
    if await AuthService.verify_permission(0, user):
        return appService.available_user(user_id)
    else:
        ErrorsService().unauthorized()


@AppRouter.post("", response_model=AppBase, status_code=status.HTTP_201_CREATED)
async def create_app(
    app: AppPost,
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> AppBase:
    if await AuthService.verify_permission(0, user):
        return appService.create(app)

    else:
        ErrorsService().unauthorized()


@AppRouter.put(
    "/user/{user_id}",
    response_model=AppsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user_apps(
    user_id: int,
    apps: List[AppBase],
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> AppsResponse:
    if await AuthService.verify_permission(0, user):
        return appService.set_user_apps(user_id=user_id, apps=apps)

    else:
        ErrorsService().unauthorized()


@AppRouter.put("/{id}", response_model=AppBase, status_code=status.HTTP_200_OK)
async def update_app(
    id: int,
    app: AppPost,
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> AppBase:
    if await AuthService.verify_permission(0, user):
        return appService.update(id, app)

    else:
        ErrorsService().unauthorized()


@AppRouter.put("/{id}/{state}", response_model=AppBase, status_code=status.HTTP_200_OK)
async def on_off_permission(
    id: int,
    state: bool,
    appService: AppService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> AppBase:
    if await AuthService.verify_permission(0, user):
        return appService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
