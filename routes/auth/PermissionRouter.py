from typing import List, Union
from fastapi import APIRouter, Depends, status

from schemas.auth.FunctionSchema import FunctionBase
from schemas.auth.PermissionSchema import (
    PermissionBase,
    PermissionDetails,
    PermissionPost,
    PermissionsResponse,
)
from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from services.auth.PermissionService import PermissionService


PermissionRouter = APIRouter(tags=["Permission"], prefix="/permissions")


@PermissionRouter.get(
    "",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_permissions(
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
    active: bool = None,
    offset: int = 0,
    limit: int = 150,
    search: str = None,
    user_id: int = None,
    group_id: int = None,
) -> PermissionsResponse:
    if await AuthService.verify_permission(0, user):
        return permissionService.get(
            offset=offset,
            limit=limit,
            active=active,
            search=search,
            user_id=user_id,
            group_id=group_id,
        )
    else:
        ErrorsService().unauthorized()


@PermissionRouter.get(
    "/{id}",
    response_model=Union[PermissionBase, PermissionDetails],
    status_code=status.HTTP_200_OK,
)
async def get_permission(
    id: int,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
    functions: bool = False,
) -> Union[PermissionBase, PermissionDetails]:
    if await AuthService.verify_permission(0, user):
        return permissionService.get_id(id=id, functions=functions)
    else:
        ErrorsService().unauthorized()


@PermissionRouter.get(
    "/group/available/{group_id}",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def group_permissions_available(
    group_id: int,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionsResponse:
    if await AuthService.verify_permission(0, user):
        return permissionService.available_group(group_id)
    else:
        ErrorsService().unauthorized()


@PermissionRouter.get(
    "/user/available/{user_id}",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_permissions_available(
    user_id: int,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionsResponse:
    if await AuthService.verify_permission(0, user):
        return permissionService.available_user(user_id)
    else:
        ErrorsService().unauthorized()


@PermissionRouter.put(
    "/user/{user_id}",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user_permissions(
    user_id: int,
    permissions: List[PermissionBase],
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionsResponse:
    if await AuthService.verify_permission(0, user):
        return permissionService.set_user_permissions(
            user_id=user_id, permissions=permissions
        )

    else:
        ErrorsService().unauthorized()


@PermissionRouter.put(
    "/group/{group_id}",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_group_permissions(
    group_id: int,
    permissions: List[PermissionBase],
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionsResponse:
    if await AuthService.verify_permission(0, user):
        return permissionService.set_group_permissions(
            group_id=group_id, permissions=permissions
        )

    else:
        ErrorsService().unauthorized()


@PermissionRouter.post(
    "", response_model=PermissionBase, status_code=status.HTTP_201_CREATED
)
async def create_permission(
    permission: PermissionPost,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionBase:
    if await AuthService.verify_permission(0, user):
        return permissionService.create(permission)

    else:
        ErrorsService().unauthorized()


@PermissionRouter.put(
    "/{id}", response_model=PermissionBase, status_code=status.HTTP_200_OK
)
async def update_permission(
    id: int,
    permission: PermissionPost,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionBase:
    if await AuthService.verify_permission(0, user):
        return permissionService.update(id, permission)

    else:
        ErrorsService().unauthorized()


@PermissionRouter.put(
    "/{id}/functions", response_model=PermissionDetails, status_code=status.HTTP_200_OK
)
async def update_functions_permission(
    id: int,
    functions: List[FunctionBase],
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionDetails:
    if await AuthService.verify_permission(0, user):
        return permissionService.update_functions(id, functions)

    else:
        ErrorsService().unauthorized()


@PermissionRouter.put(
    "/{id}/{state}", response_model=PermissionBase, status_code=status.HTTP_200_OK
)
async def on_off_permission(
    id: int,
    state: bool,
    permissionService: PermissionService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> PermissionBase:
    if await AuthService.verify_permission(0, user):
        return permissionService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
