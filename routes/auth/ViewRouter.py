from typing import List, Union
from fastapi import APIRouter, Depends, status
from schemas.auth.ViewSchema import ViewBase, ViewPost, ViewsResponse
from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from services.auth.ViewService import ViewService


ViewRouter = APIRouter(tags=["View"], prefix="/view")


@ViewRouter.get(
    "",
    response_model=ViewsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_views(
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
    active: bool = None,
    offset: int = 0,
    limit: int = 150,
    user_id: int = None,
    app_id: int = None,
) -> ViewsResponse:
    if await AuthService.verify_permission(0, user):
        return viewService.get(
            offset=offset, limit=limit, active=active, app_id=app_id, user_id=user_id
        )
    else:
        ErrorsService().unauthorized()


@ViewRouter.get(
    "/{id}",
    response_model=ViewBase,
    status_code=status.HTTP_200_OK,
)
async def get_view(
    id: int,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewBase:
    if await AuthService.verify_permission(0, user):
        return viewService.get_id(id=id)
    else:
        ErrorsService().unauthorized()


@ViewRouter.get(
    "/app/available/{app_id}",
    response_model=ViewsResponse,
    status_code=status.HTTP_200_OK,
)
async def app_views_available(
    app_id: int,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewsResponse:
    if await AuthService.verify_permission(0, user):
        return viewService.available_app(app_id)
    else:
        ErrorsService().unauthorized()


@ViewRouter.get(
    "/user/available/{user_id}",
    response_model=ViewsResponse,
    status_code=status.HTTP_200_OK,
)
async def app_views_available(
    user_id: int,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewsResponse:
    if await AuthService.verify_permission(0, user):
        return viewService.available_user(user_id)
    else:
        ErrorsService().unauthorized()


@ViewRouter.post("", response_model=ViewBase, status_code=status.HTTP_201_CREATED)
async def create_view(
    view: ViewPost,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewBase:
    if await AuthService.verify_permission(0, user):
        return viewService.create(view)

    else:
        ErrorsService().unauthorized()


@ViewRouter.put(
    "/user/{user_id}",
    response_model=ViewsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user_views(
    user_id: int,
    views: List[ViewBase],
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewsResponse:
    if await AuthService.verify_permission(0, user):
        return viewService.set_user_views(user_id=user_id, views=views)

    else:
        ErrorsService().unauthorized()


@ViewRouter.put(
    "/app/{app_id}",
    response_model=ViewsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_app_views(
    app_id: int,
    views: List[ViewBase],
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewsResponse:
    if await AuthService.verify_permission(0, user):
        return viewService.set_app_views(app_id=app_id, views=views)

    else:
        ErrorsService().unauthorized()


@ViewRouter.put("/{id}", response_model=ViewBase, status_code=status.HTTP_200_OK)
async def update_permission(
    id: int,
    view: ViewPost,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewBase:
    if await AuthService.verify_permission(0, user):
        return viewService.update(id, view)

    else:
        ErrorsService().unauthorized()


@ViewRouter.put(
    "/{id}/{state}", response_model=ViewBase, status_code=status.HTTP_200_OK
)
async def on_off_permission(
    id: int,
    state: bool,
    viewService: ViewService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> ViewBase:
    if await AuthService.verify_permission(0, user):
        return viewService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
