from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas.token import TokenData
from utils.settings import Settings

from config.db import conn, session
from models.user.user import user
from models.user_permission_group.user_permission_group import user_permission_group
from models.permission_function.permission_function import permission_function
from models.permission.permission import permission

settings = Settings()


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def verify_user(email):
    email = str(email)
    user_current = conn.execute(user.select().where(
        user.c.email == email)).first()
    if user_current:
        return user_current
    else:
        return False


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: TokenData, type_user):
    if (type_user == 'user_platform'):
        user_current = [{
            'id': data[0],
            'email': data[4],
            'exp': str(datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
            'isAutenticated': True,
            'user_group': data[10],
            'type': 'user_platform'

        }]
        encoded_jwt = jwt.encode(
            {'data': user_current}, SECRET_KEY, algorithm=ALGORITHM)
        user_current[0]['access_token'] = encoded_jwt
        return user_current[0]


async def validate_access_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


async def validate_email(token: str):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return token['data'][0]

    except JWTError:
        raise credentials_exception


async def verify_permission(user_current: object, function: int):
    if user_current['type'] == 'user_platform':

        permission_asociated = conn.execute(permission_function.select().where(
            permission_function.c.function_id == function)).first()

        if permission_asociated:
            permission_current = conn.execute(permission.select()
                                              .where(permission.c.id == permission_asociated.permission_id)).first()

            group_permissions = session.query(
                user_permission_group,
                permission
            ).join(
                permission, permission.c.id == user_permission_group.c.permission_id
            ).filter(user_permission_group.c.group_id == user_current['user_group']).filter(
                permission.c.name == permission_current.name).first()

            if group_permissions:
                session.close()
                return True

            user_permissions = session.query(
                user_permission_group,
                permission
            ).join(
                permission, permission.c.id == user_permission_group.c.permission_id
            ).filter(user_permission_group.c.user_id == user_current['id']).filter(
                permission.c.name == permission_current.name).first()

            if user_permissions:
                session.close()
                return True

        else:
            return True
    else:
        return False
