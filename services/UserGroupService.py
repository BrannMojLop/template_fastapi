import re
from typing import List, Union
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from models.Permission import Permission
from models.UserGroup import UserGroup
from fastapi.encoders import jsonable_encoder
from models.UserPermissionGroup import UserPermissionGroup
from schemas.PermissionSchema import PermissionBase
from schemas.UserGroupSchema import (
    UserGroupBase,
    UserGroupDetails,
    UserGroupModeSelect,
    UserGroupPost,
    UserGroupsResponse,
)
from services.ErrorsService import ErrorsService


class UserGroupService:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get(
        self,
        offset: int = 0,
        limit: int = 150,
        active: bool = None,
        mode_select: bool = False,
        search: str = None,
    ) -> Union[List[UserGroupModeSelect], UserGroupsResponse]:
        try:
            query = self.db.query(UserGroup)

            if active is not None:
                query = query.filter(UserGroup.is_active == active)

            if search is not None:
                query = query.filter(UserGroup.name.ilike(f"%{search}%"))

            if mode_select:
                users_groups = query.all()
                users_groups_select = []
                for user_group in users_groups:
                    users_groups_select.append(
                        {"label": user_group.name, "value": user_group.id}
                    )
                return jsonable_encoder(users_groups_select)

            total = query.count()
            users_groups = query.offset(offset).limit(limit).all()

            return UserGroupsResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=jsonable_encoder(users_groups),
            )

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(
        self, id: int, permissions: bool = False
    ) -> Union[UserGroupBase, UserGroupDetails]:
        try:
            group = self.db.query(UserGroup).filter(UserGroup.id == id).first()

            if not group:
                ErrorsService().not_found(
                    loc="query",
                    label="user group",
                    value=id,
                )

            if permissions:
                group_permissions = (
                    self.db.query(Permission)
                    .filter(UserPermissionGroup.group_id == id)
                    .join(
                        UserPermissionGroup,
                        Permission.id == UserPermissionGroup.permission_id,
                    )
                    .all()
                )
                return UserGroupDetails(group=group, permissions=group_permissions)

            return group

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, group: UserGroupPost) -> UserGroupBase:
        try:
            new_group = UserGroup(**group.dict())
            self.db.add(new_group)
            self.db.commit()

            return new_group

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=group.name)

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, group: UserGroupPost) -> UserGroupBase:
        try:
            result = self.get_id(id)

            for key, value in group.dict(exclude_unset=True).items():
                setattr(result, key, value)

            self.db.commit()

            return result

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=group.name)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> UserGroupBase:
        try:
            group = self.db.query(UserGroup).filter(UserGroup.id == id).first()

            if not group:
                ErrorsService().not_found(
                    loc="query",
                    label="user group",
                    value=id,
                )

            group.is_active = state
            self.db.commit()

            return group

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update_permissions(
        self, id: int, permissions: List[PermissionBase]
    ) -> UserGroupDetails:
        try:
            user_group = self.get_id(id)

            permissions_group = (
                self.db.query(UserPermissionGroup)
                .filter(UserPermissionGroup.group_id == id)
                .all()
            )

            for permission in permissions:
                add = True

                for permission_group in permissions_group:
                    if permission.id == permission_group.permission_id:
                        add = False
                        break

                if add:
                    self.db.add(
                        UserPermissionGroup(group_id=id, permission_id=permission.id)
                    )

            for permission_group in permissions_group:
                remove = True

                for permission in permissions:
                    if permission.id == permission_group.permission_id:
                        remove = False
                        break

                if remove:
                    self.db.delete(permission_group)

            self.db.commit()

            return UserGroupDetails(group=user_group, permissions=permissions)

        except SQLAlchemyError as e:
            error_msg = str(e)

            match = re.search(r"permission_id': (\d+)", error_msg)
            if match:
                permission_id = int(match.group(1))
                ErrorsService().not_found(
                    label="permission_id", loc="body", value=permission_id
                )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
