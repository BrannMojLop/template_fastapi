import re
from pydantic import BaseModel, field_validator
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.User import User

UserBaseModel = sqlalchemy_to_pydantic(User)

UserModel = sqlalchemy_to_pydantic(
    User,
    exclude={"password_version", "password_hash", "access_version", "password_temp"},
)


class UserBase(UserModel):
    pass


class UserNormalized(UserBase):
    user_group_name: str | None = None


class UsersResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[UserNormalized]


class UserModeSelect(BaseModel):
    label: str
    value: int


class UserForId(BaseModel):
    id: UserBase  # type: ignore


class UserPost(BaseModel):
    username: str
    first_name: str
    last_name: str
    password_hash: str | None = None
    email: str | None = None
    phone: str | None = None

    @field_validator("email")
    def validate_email(cls, value):
        if not value:
            return None

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email address")

        return value.lower()

    @field_validator("phone")
    def phone_validate(cls, value):
        if not value:
            return None

        if value.isdigit():
            return value

        raise ValueError("The 'phone' parameter is not a phone number valid")


class UserUpdate(UserPost):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserPostLogin(BaseModel):
    user: str
    password: str


class UserChangePassword(BaseModel):
    password: str


class UserAccessToken(BaseModel):
    id: int
    email: str | None = None
    name: str
    phone: str | None = None
    user_group: int | None = None
    apps: list[str]
    views: list[str]
    apps_views: object | None = None
    password_temp: bool
    password_version: int
    access_version: int
    access_token: str
    exp: str


class UserValidateToken(UserAccessToken):
    access_token: str | None = None
