import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings(BaseSettings):
    secret_key: str = os.getenv("SECRET_KEY")
    token_expire: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    db_host: str = os.getenv("HOST_DB")
    db_username: str = os.getenv("USERNAME_DB")
    db_password: str = os.getenv("PASSWORD_DB")
    db_name: str = os.getenv("DATABASE")
    db_port: str = os.getenv("PORT_DB")
    url: str = os.getenv("BASE_URL")
    email: str = os.getenv("EMAIL")
    email_password: str = os.getenv("PASSWORD_EMAIL")
    aws_bucket: str = os.getenv("AWS_BUCKET")
    aws_path: str = os.getenv("AWS_PATH")
    tests_token: str = os.getenv("TESTS_TOKEN")
