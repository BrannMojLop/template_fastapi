from typing import List
from fastapi import APIRouter, Depends, status

from schemas.auth.FunctionSchema import FunctionBase, FunctionsResponse

from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from services.auth.FunctionsService import FunctionsService

FunctionsRouter = APIRouter(tags=["Functions"], prefix="/functions")


@FunctionsRouter.get(
    "",
    response_model=FunctionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_functions(
    functionsService: FunctionsService = Depends(),
    user=Depends(AuthService.validate_access_token),
    available: bool = None,
    offset: int = 0,
    limit: int = 150,
    search: str = None,
    permission: int = None,
) -> FunctionsResponse:
    if await AuthService.verify_permission(0, user):
        return functionsService.get(
            offset=offset,
            limit=limit,
            search=search,
            available=available,
            permission=permission,
        )
    else:
        ErrorsService().unauthorized()


@FunctionsRouter.get(
    "/{id}",
    response_model=FunctionBase,
    status_code=status.HTTP_200_OK,
)
async def get_functions(
    id: int,
    functionsService: FunctionsService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> FunctionBase:
    if await AuthService.verify_permission(0, user):
        return functionsService.get_id(id)
    else:
        ErrorsService().unauthorized()


@FunctionsRouter.put(
    "/permission/{permission}",
    response_model=FunctionsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_group_permissions(
    permission: int,
    functions: List[FunctionBase],
    functionsService: FunctionsService = Depends(),
    user=Depends(AuthService.validate_access_token),
) -> FunctionsResponse:
    if await AuthService.verify_permission(0, user):
        return functionsService.set_functions(
            permission=permission, functions=functions
        )

    else:
        ErrorsService().unauthorized()
