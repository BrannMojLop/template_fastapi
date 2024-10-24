import re
from typing import List, Union
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from models.auth.User import User
from schemas.auth.UserSchema import (
    UserAccessToken,
    UserBase,
    UserModeSelect,
    UserNormalized,
    UserPost,
    UserUpdate,
    UsersResponse,
)
from services.auth.AuthService import AuthService
from services.auth.ErrorsService import ErrorsService
from utils.password_generate import password_generate, get_password_hash
from utils.records_by_id import RecordsByID
from utils.records_validate import RecordsValiate


class UserService:
    def __init__(
        self,
        db: Session = Depends(get_db_connection),
    ):
        self.db = db

    def get(
        self,
        active: bool = None,
        offset: int = 0,
        limit: int = 150,
        search: str = None,
        mode_select: bool = False,
        group: int = None,
    ) -> Union[List[UserModeSelect], UsersResponse]:
        try:
            query = self.db.query(User)

            if active is not None:
                query = query.filter(User.is_active == active)

            if group is not None:
                query = query.filter(User.user_group == group)

            if search is not None:
                query = query.filter(
                    or_(
                        User.first_name.ilike(f"%{search}%"),
                        User.last_name.ilike(f"%{search}%"),
                    )
                )

            if mode_select:
                users = query.all()
                users_select = []
                for user in users:
                    users_select.append(
                        {
                            "label": f"{user.first_name} {user.last_name}",
                            "value": user.id,
                        }
                    )

                return jsonable_encoder(users_select)

            total = query.count()
            query = query.offset(offset).limit(limit).all()
            users = []

            records_by_id = RecordsByID(self.db)
            groups = records_by_id.user_groups()

            for row in query:
                user = row.__dict__

                if row.user_group:
                    user["user_group_name"] = groups[row.user_group].name

                users.append(user)

            return UsersResponse(offset=offset, limit=limit, total=total, data=users)

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(self, id: int, exception: bool = True) -> UserNormalized:
        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                if exception:
                    ErrorsService().not_found(
                        loc="query",
                        label="user",
                        value=id,
                    )
                else:
                    return None

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, user_form: UserPost) -> UserBase:
        try:
            new_password = password_generate(8)
            password_hash = get_password_hash(new_password)

            new_user = user_form.model_dump()
            new_user["password_hash"] = password_hash
            new_user["password_temp"] = new_password

            new_user = User(**new_user)

            self.db.add(new_user)
            self.db.commit()

            return new_user

        except SQLAlchemyError as e:
            error_msg = str(e)

            match = re.search(
                r"Duplicate entry '(?P<value_duplicate>.+)' for key '(?P<column>.+)'",
                error_msg,
            )

            if match:
                value = match.group("value_duplicate")
                label = match.group("column")
                ErrorsService().duplicate_entry(label=label, value=value)

            if "foreign key constraint fails" in error_msg:
                ErrorsService().not_found(
                    label="user_group",
                    value=user_form.user_group,
                    loc="body",
                )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, user_update: UserUpdate) -> UserNormalized:
        try:
            recordsValidate = RecordsValiate(db=self.db)

            user = recordsValidate.user(id=id)

            for key, value in user_update.dict(exclude_unset=True).items():
                setattr(user, key, value)

            self.db.commit()

            return user

        except SQLAlchemyError as e:
            error_msg = str(e)

            match = re.search(
                r"Duplicate entry '(?P<value_duplicate>.+)' for key '(?P<column>.+)'",
                error_msg,
            )

            if match:
                value = match.group("value_duplicate")
                label = match.group("column")
                ErrorsService().duplicate_entry(label=label, value=value)

            if "foreign key constraint fails" in error_msg:
                ErrorsService().not_found(
                    label="user_group",
                    value=user_update.user_group,
                    loc="body",
                )

        except HTTPException as http_exc:
            raise http_exc

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> UserNormalized:
        try:
            recordsValidate = RecordsValiate(db=self.db)
            user = recordsValidate.user(id=id)
            user.is_active = state
            self.db.commit()

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    async def change_password(self, id: int, password: str) -> UserAccessToken:
        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            password_hash = get_password_hash(password)

            user.password_hash = password_hash
            user.password_temp = None
            user.password_version = user.password_version + 1

            auth_new_service = AuthService(**user.__dict__)
            access_token = await auth_new_service.create_access_token()

            self.db.commit()
            return access_token

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def next_access_version(self, id: int):
        """Updates the access_version attribute (+1)

        Args:
            id (int): User ID
        """

        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            user.access_version = user.access_version + 1
            self.db.commit()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def reset_password(self, id: int) -> UserNormalized:
        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            new_password = password_generate(8)

            password_hash = get_password_hash(new_password)

            user.password_hash = password_hash
            user.password_temp = new_password

            self.db.commit()

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
