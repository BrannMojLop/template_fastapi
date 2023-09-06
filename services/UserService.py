import re
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from fastapi.encoders import jsonable_encoder
from models.User import TypeUser, User
from schemas.UserSchema import UserBase, UserPost, UserResponse, UserUpdate
from services.ErrorsService import ErrorsService
from services.AuthService import AuthService
from utils.password_generate import password_generate
from utils.records_by_id import RecordsByID
from utils.records_validate import RecordsValiate


class UserService:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get(
        self, offset: int = 0, limit: int = 150, type: TypeUser = None
    ) -> UserResponse:
        try:
            query = self.db.query(User)

            if type is not None:
                query = query.filter(User.type == type)

            total = query.count()
            response = query.offset(offset).limit(limit).all()

            groups = RecordsByID(db=self.db).user_groups()
            response_format = []

            for user in response:
                user_format = user.__dict__

                if user.user_group:
                    user_format["user_group_name"] = groups[user.user_group].name

                response_format.append(user_format)

            return UserResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=response_format,
            )

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(self, id: int) -> UserBase:
        try:
            query = self.db.query(User).filter(User.id == id).first()

            if not query:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            return jsonable_encoder(query)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, user_form: UserPost) -> UserBase:
        try:
            if user_form.user_group == 0:
                user_form.user_group = None

            authService = AuthService(**user_form.__dict__)
            new_password = password_generate(8)
            password_hash = authService.get_password_hash(new_password)

            new_user = user_form.dict()
            new_user["password_hash"] = password_hash
            new_user["password_temp"] = new_password

            add_user = User(**new_user)

            self.db.add(add_user)
            self.db.commit()

            return add_user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, user_update: UserUpdate) -> UserBase:
        try:
            recordsValidate = RecordsValiate(db=self.db)

            if user_update.user_group == 0:
                user_update.user_group = None

            user = recordsValidate.user(id)

            for key, value in user_update.dict(exclude_unset=True).items():
                setattr(user, key, value)

            self.db.commit()

            return user

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                if "user.email" in error_msg:
                    ErrorsService().duplicate_entry(
                        label="email", value=user_update.email
                    )

                if "user.phone" in error_msg:
                    ErrorsService().duplicate_entry(
                        label="phone", value=user_update.phone
                    )

            match = re.search(r"user_group': (\d+)", error_msg)

            if match:
                group_id = int(match.group(1))
                ErrorsService().not_found(label="group_id", loc="body", value=group_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> UserBase:
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

    def change_password(self, id: int, password: str) -> UserBase:
        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            authService = AuthService(**user.__dict__)
            password_hash = authService.get_password_hash(password)

            user.password_hash = password_hash
            user.password_temp = None
            user.password_version = user.password_version + 1

            self.db.commit()

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def reset_password(self, id: int) -> UserBase:
        try:
            user = self.db.query(User).filter(User.id == id).first()

            if not user:
                ErrorsService().not_found(
                    loc="query",
                    label="user",
                    value=id,
                )

            new_password = password_generate(8)

            authService = AuthService(**user.__dict__)
            password_hash = authService.get_password_hash(new_password)

            user.password_hash = password_hash
            user.password_temp = new_password
            user.password_version = user.password_version + 1

            self.db.commit()

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
