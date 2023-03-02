import os

from pydantic import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):

    secret_key: str = os.getenv('SECRET_KEY')
    token_expire: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    db_host: str = os.getenv('HOST')
    db_username: str = os.getenv('USERNAME_DB')
    db_password: str = os.getenv('PASSWORD')
    db_name: str = os.getenv('DATABASE')
    db_port: str = os.getenv('PORT')
    ngrok: str = os.getenv('USE_NGROK')
    url: str = os.getenv('BASE_URL')
    email: str = os.getenv('EMAIL')
    email_password: str = os.getenv('PASSWORD_EMAIL')
