from passlib.context import CryptContext
from random import choice


def password_generate(large):
    values = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
    password = ""
    password = password.join([choice(values) for i in range(large)])
    return password


def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
