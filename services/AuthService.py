from datetime import datetime, timedelta
from models.Permission import Permission
from models.User import User
from models.UserPermissionGroup import UserPermissionGroup
from services.ErrorsService import ErrorsService
from utils.settings import Settings
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config.Database import SessionLocal
from passlib.context import CryptContext
from schemas.UserSchema import (
    UserAccessToken,
    UserValidateToken,
    UserBaseAuth,
)
from models.PermissionFunction import PermissionFunction

settings = Settings()


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire
BASE_URL = settings.url

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{BASE_URL}/token")


class AuthService(UserBaseAuth):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify_password(self, plain_password) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    async def create_access_token(self) -> UserAccessToken:
        user = {
            "id": self.id,
            "name": f"{self.name} {self.last_name_first} {self.last_name_second}",
            "email": self.email,
            "phone": self.phone,
            "type": self.type.value,
            "password_temp": self.password_temp is not None if True else False,
            "password_version": self.password_version,
            "exp": str(
                datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            ),
            "user_group": self.user_group,
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

            if (
                user.is_active
                and user.password_version == token_data["password_version"]
            ):
                if not token_data["password_temp"]:
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

    async def validate_change_password(
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

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

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
