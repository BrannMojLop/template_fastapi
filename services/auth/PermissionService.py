import re
from typing import List, Union
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from models.auth.Function import Function
from models.auth.Permission import Permission
from fastapi.encoders import jsonable_encoder
from models.auth.PermissionFunction import PermissionFunction
from models.auth.UserPermissionGroup import UserPermissionGroup
from schemas.auth.FunctionSchema import FunctionBase
from schemas.auth.PermissionSchema import (
    PermissionBase,
    PermissionDetails,
    PermissionPost,
    PermissionsResponse,
)
from services.auth.ErrorsService import ErrorsService
from services.auth.FunctionsService import FunctionsService
from utils.records_validate import RecordsValiate


class PermissionService:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get(
        self,
        active: bool = None,
        offset: int = 0,
        limit: int = 150,
        search: str = None,
        user_id: int = None,
        group_id: int = None,
    ) -> PermissionsResponse:
        try:
            query = self.db.query(Permission)

            if search is not None:
                query = query.filter(Permission.name.ilike(f"%{search}%"))

            if active is not None:
                query = query.filter(Permission.is_active == active)

            if user_id is not None:
                query = query.join(
                    UserPermissionGroup,
                    UserPermissionGroup.permission_id == Permission.id,
                ).filter(UserPermissionGroup.user_id == user_id)

            if group_id is not None:
                query = query.join(
                    UserPermissionGroup,
                    UserPermissionGroup.permission_id == Permission.id,
                ).filter(UserPermissionGroup.group_id == group_id)

            total = query.count()
            permissions = query.offset(offset).limit(limit).all()

            return PermissionsResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=jsonable_encoder(permissions),
            )

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(
        self, id: int, functions: bool = False
    ) -> Union[PermissionBase, PermissionDetails]:
        try:
            permission = self.db.query(Permission).filter(Permission.id == id).first()

            if not permission:
                ErrorsService().not_found(
                    loc="query",
                    label="permission",
                    value=id,
                )

            if functions:
                functions_permission = (
                    self.db.query(Function)
                    .filter(PermissionFunction.permission_id == id)
                    .join(
                        PermissionFunction,
                        PermissionFunction.function_id == Function.id,
                    )
                    .all()
                )

                return PermissionDetails(
                    permission=permission, functions=functions_permission
                )

            return permission

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def available_group(self, group_id: int) -> PermissionsResponse:
        try:
            permissions_group = (
                self.db.query(UserPermissionGroup)
                .filter(UserPermissionGroup.group_id == group_id)
                .all()
            )

            permissions = self.get(active=True)

            if len(permissions_group):
                permissions_avaible = []

                for permission in permissions.data:
                    available = True

                    for permission_group in permissions_group:
                        if permission.id == permission_group.permission_id:
                            available = False
                            break

                    if available:
                        permissions_avaible.append(permission)

                return PermissionsResponse(
                    offset=0,
                    limit=len(permissions_avaible),
                    total=len(permissions_avaible),
                    data=permissions_avaible,
                )

            else:
                return permissions

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def available_user(self, user_id: int) -> PermissionsResponse:
        try:
            recordsValiate = RecordsValiate(db=self.db)
            user = recordsValiate.user(user_id)

            permissions_user = (
                self.db.query(UserPermissionGroup)
                .filter(UserPermissionGroup.user_id == user_id)
                .all()
            )

            permissions_group = []

            if user.user_group:
                permissions_group = (
                    self.db.query(UserPermissionGroup)
                    .filter(UserPermissionGroup.group_id == user.user_group)
                    .all()
                )

            permissions = self.get(active=True)

            if len(permissions_group) or len(permissions_user):
                permissions_avaible = []

                for permission in permissions.data:
                    available = True

                    for permission_user in permissions_user:
                        if permission.id == permission_user.permission_id:
                            available = False
                            break

                    if available:
                        for permission_group in permissions_group:
                            if permission.id == permission_group.permission_id:
                                available = False
                                break

                    if available:
                        permissions_avaible.append(permission)

                return PermissionsResponse(
                    offset=0,
                    limit=len(permissions_avaible),
                    total=len(permissions_avaible),
                    data=permissions_avaible,
                )

            else:
                return permissions

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, permission: PermissionPost) -> PermissionBase:
        try:
            new_permission = Permission(**permission.dict())
            self.db.add(new_permission)
            self.db.commit()

            return new_permission

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=permission.name)

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, permission: PermissionPost) -> PermissionBase:
        try:
            result = self.get_id(id)

            for key, value in permission.dict(exclude_unset=True).items():
                setattr(result, key, value)

            self.db.commit()

            return result

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=permission.name)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_user_permissions(
        self,
        user_id: int,
        permissions: List[PermissionBase],
    ) -> PermissionsResponse:
        try:
            permissions_user = (
                self.db.query(UserPermissionGroup)
                .filter(UserPermissionGroup.user_id == user_id)
                .all()
            )

            for per in permissions:
                add = True

                for per_user in permissions_user:
                    if per.id == per_user.permission_id:
                        add = False
                        break

                if add:
                    new_permission = UserPermissionGroup(
                        user_id=user_id, permission_id=per.id
                    )

                    self.db.add(new_permission)

            for per_user in permissions_user:
                remove = True

                for per in permissions:
                    if per.id == per_user.permission_id:
                        remove = False
                        break

                if remove:
                    self.db.delete(per_user)

            self.db.commit()

            return self.get(active=True, user_id=user_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_group_permissions(
        self, group_id: int, permissions: List[PermissionBase]
    ) -> PermissionsResponse:
        try:
            permissions_group = (
                self.db.query(UserPermissionGroup)
                .filter(UserPermissionGroup.group_id == group_id)
                .all()
            )

            for per in permissions:
                add = True
                if len(permissions_group):
                    for per_group in permissions_group:
                        if per.id == per_group.permission_id:
                            add = False
                            break

                if add:
                    new_permission = UserPermissionGroup(
                        group_id=group_id, permission_id=per.id
                    )
                    self.db.add(new_permission)

            for per_group in permissions_group:
                remove = True
                if len(permissions):
                    for per in permissions:
                        if per.id == per_group.permission_id:
                            remove = False
                            break

                if remove:
                    self.db.delete(per_group)

            self.db.commit()

            return self.get(active=True, user_id=group_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update_functions(
        self, id: int, functions: List[FunctionBase]
    ) -> PermissionDetails:
        try:
            permission = self.get_id(id)

            functions_permission = (
                self.db.query(PermissionFunction)
                .filter(PermissionFunction.permission_id == id)
                .all()
            )

            for permission in functions:
                add = True

                for function_permission in functions_permission:
                    if permission.id == function_permission.function_id:
                        add = False
                        break

                if add:
                    self.db.add(
                        PermissionFunction(permission_id=id, function_id=permission.id)
                    )

            for function_permission in functions_permission:
                remove = True

                for permission in functions:
                    if permission.id == function_permission.function_id:
                        remove = False
                        break

                if remove:
                    self.db.delete(function_permission)

            self.db.commit()

            return PermissionDetails(permission=permission, functions=functions)

        except SQLAlchemyError as e:
            error_msg = str(e)

            match = re.search(r"function_id': (\d+)", error_msg)

            if match:
                function_id = int(match.group(1))
                ErrorsService().not_found(
                    loc="body", label="function_id", value=function_id
                )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> PermissionBase:
        try:
            permission = self.db.query(Permission).filter(Permission.id == id).first()

            if not permission:
                ErrorsService().not_found(
                    loc="query",
                    label="permission_id",
                    value=id,
                )

            if not state:
                FunctionsService(db=self.db).set_functions(permission=id, functions=[])

            permission.is_active = state
            self.db.commit()

            return permission

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
