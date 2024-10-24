from datetime import datetime, timedelta
from models.auth.App import App
from models.auth.AppUser import AppUser
from models.auth.AppViewUser import AppViewUser
from models.auth.Permission import Permission
from models.auth.User import User
from models.auth.UserPermissionGroup import UserPermissionGroup
from models.auth.View import View
from services.auth.ErrorsService import ErrorsService
from utils.settings import Settings
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config.Database import SessionLocal
from passlib.context import CryptContext
from schemas.auth.UserSchema import (
    UserAccessToken,
    UserValidateToken,
    UserBaseModel,
)
from models.auth.PermissionFunction import PermissionFunction

settings = Settings()


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire
BASE_URL = settings.url

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{BASE_URL}/token")


class AuthService(UserBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify_password(self, plain_password) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    async def create_access_token(self) -> UserAccessToken:
        apps = (
            SessionLocal.query(App)
            .join(
                AppUser,
                AppUser.app_id == App.id,
            )
            .filter(AppUser.user_id == self.id)
            .filter(App.is_active)
            .order_by(AppUser.id)
            .all()
        )

        views = (
            SessionLocal.query(View)
            .join(
                AppViewUser,
                AppViewUser.view_id == View.id,
            )
            .filter(AppViewUser.user_id == self.id)
            .filter(View.is_active)
            .order_by(AppViewUser.id)
            .all()
        )

        apps_list = [app.get_name() for app in apps]
        views_prev_list = [view.get_name() for view in views]
        apps_views = {}
        apps_views_set = set()

        for app in apps:
            views = (
                SessionLocal.query(View)
                .join(
                    AppViewUser,
                    AppViewUser.view_id == View.id,
                )
                .filter(AppViewUser.app_id == app.id)
                .filter(View.is_active)
                .all()
            )

            serialized_views = [view.get_name() for view in views]
            views_prev_list += serialized_views
            apps_views[app.name] = serialized_views

            apps_views_set.update(serialized_views)

        views_set = set(views_prev_list)
        others_views = views_set.symmetric_difference(apps_views_set)

        if len(others_views):
            apps_list.append("other")
            apps_views["other"] = list(others_views)

        views_list = list(views_set)

        user = {
            "id": self.id,
            "name": f"{self.first_name} {self.last_name}",
            "email": self.email,
            "phone": self.phone,
            "password_temp": self.password_temp != None if True else False,
            "password_version": self.password_version,
            "access_version": self.access_version,
            "user_group": self.user_group,
            "apps": apps_list,
            "views": views_list,
            "apps_views": apps_views,
            "exp": str(
                datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            ),
        }

        encoded_jwt = jwt.encode({"data": [user]}, SECRET_KEY, algorithm=ALGORITHM)
        user["access_token"] = encoded_jwt
        return UserAccessToken(**user)

    async def validate_access_token(
        token: str = Depends(oauth2_scheme),
    ) -> UserValidateToken:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = payload["data"][0]

            user = SessionLocal.query(User).filter(User.id == token_data["id"]).first()

            if not user:
                raise ErrorsService().credentials_token()

            if not user.is_active:
                raise ErrorsService().update_token()

            if user.password_temp or token_data["password_temp"]:
                raise ErrorsService().password_temp()

            if (
                not "access_version" in token_data
                or not user.access_version == token_data["access_version"]
            ):
                raise ErrorsService().update_token()

            if (
                not "password_version" in token_data
                or not user.password_version == token_data["password_version"]
            ):
                raise ErrorsService().update_token()

            if (
                datetime.strptime(token_data["exp"], "%Y-%m-%d %H:%M:%S.%f")
                < datetime.now()
            ):
                raise ErrorsService().update_token()

            return UserValidateToken(**token_data)

        except JWTError:
            raise ErrorsService().credentials_token()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

        finally:
            SessionLocal.close()

    async def validate_change_password_temp(
        token: str = Depends(oauth2_scheme),
    ) -> UserValidateToken:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = payload["data"][0]

            user = SessionLocal.query(User).filter(User.id == token_data["id"]).first()

            if (
                user.is_active
                and user.password_version == token_data["password_version"]
                and user.password_temp
            ):
                return UserValidateToken(**token_data)

            raise ErrorsService().credentials_token()

        except JWTError:
            raise ErrorsService().credentials_token()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

        finally:
            SessionLocal.close()

    async def validate_email(token: str) -> UserValidateToken:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = payload["data"][0]
            return UserValidateToken(**user)

        except JWTError:
            raise ErrorsService().credentials_token()

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    async def verify_permission(function: int, token_data: UserAccessToken) -> bool:
        try:
            permission_asociated = (
                SessionLocal.query(PermissionFunction)
                .filter(PermissionFunction.function_id == function)
                .first()
            )

            if permission_asociated:
                user = SessionLocal.query(User).filter(User.id == token_data.id).first()

                permission_current = (
                    SessionLocal.query(Permission)
                    .filter(Permission.id == permission_asociated.permission_id)
                    .first()
                )

                if permission_current.is_active:
                    group_permissions = False

                    if user.user_group:
                        group_permissions = (
                            SessionLocal.query(UserPermissionGroup, Permission)
                            .join(
                                Permission,
                                Permission.id == UserPermissionGroup.permission_id,
                            )
                            .filter(UserPermissionGroup.group_id == user.user_group)
                            .filter(Permission.name == permission_current.name)
                            .first()
                        )

                    if group_permissions:
                        return True

                    user_permissions = (
                        SessionLocal.query(UserPermissionGroup, Permission)
                        .join(
                            Permission,
                            Permission.id == UserPermissionGroup.permission_id,
                        )
                        .filter(UserPermissionGroup.user_id == user.id)
                        .filter(Permission.name == permission_current.name)
                        .first()
                    )

                    if user_permissions:
                        return True
                else:
                    return False
            else:
                return True

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

        finally:
            SessionLocal.close()
