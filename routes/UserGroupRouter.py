from typing import List, Union
from fastapi import APIRouter, Depends, status

from schemas.PermissionSchema import PermissionBase
from schemas.UserGroupSchema import (
    UserGroupBase,
    UserGroupDetails,
    UserGroupModeSelect,
    UserGroupPost,
    UserGroupsResponse,
)
from services.AuthService import AuthService
from services.ErrorsService import ErrorsService
from services.UserGroupService import UserGroupService


UserGroupRouter = APIRouter(tags=["UserGroup"], prefix="/users/group")


@UserGroupRouter.get(
    "",
    response_model=Union[List[UserGroupModeSelect], UserGroupsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_users_groups(
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
    active: bool = None,
    offset: int = 0,
    limit: int = 150,
    mode_select: bool = False,
    search: str = None,
) -> Union[List[UserGroupModeSelect], UserGroupsResponse]:
    if await AuthService.verify_permission(0, user):
        return userGroupService.get(
            offset=offset,
            limit=limit,
            active=active,
            mode_select=mode_select,
            search=search,
        )
    else:
        ErrorsService().unauthorized()


@UserGroupRouter.get(
    "/{id}",
    response_model=Union[UserGroupBase, UserGroupDetails],
    status_code=status.HTTP_200_OK,
)
async def get_user_group(
    id: int,
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
    permissions: bool = False,
) -> Union[UserGroupBase, UserGroupDetails]:
    if await AuthService.verify_permission(0, user):
        return userGroupService.get_id(id, permissions=permissions)
    else:
        ErrorsService().unauthorized()


@UserGroupRouter.post(
    "", response_model=UserGroupBase, status_code=status.HTTP_201_CREATED
)
async def create_user_group(
    group: UserGroupPost,
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserGroupBase:
    if await AuthService.verify_permission(0, user):
        return userGroupService.create(group)

    else:
        ErrorsService().unauthorized()


@UserGroupRouter.put(
    "/{id}", response_model=UserGroupBase, status_code=status.HTTP_200_OK
)
async def update_user_group(
    id: int,
    group: UserGroupPost,
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserGroupBase:
    if await AuthService.verify_permission(0, user):
        return userGroupService.update(id, group)

    else:
        ErrorsService().unauthorized()


@UserGroupRouter.put("/{id}/permissions", status_code=status.HTTP_200_OK)
async def update_permissions_user_group(
    id: int,
    permissions: List[PermissionBase],
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
):
    if await AuthService.verify_permission(0, user):
        return userGroupService.update_permissions(id, permissions)

    else:
        ErrorsService().unauthorized()


@UserGroupRouter.put(
    "/{id}/{state}", response_model=UserGroupBase, status_code=status.HTTP_200_OK
)
async def on_off_group(
    id: int,
    state: bool,
    userGroupService: UserGroupService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> UserGroupBase:
    if await AuthService.verify_permission(0, user):
        return userGroupService.on_off(id=id, state=state)

    else:
        ErrorsService().unauthorized()
