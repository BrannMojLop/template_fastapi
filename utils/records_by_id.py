from typing import List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi import Depends
from config.Database import get_db_connection
from models.auth.User import User
from models.auth.UserGroup import UserGroup
from schemas.auth.UserGroupSchema import UserGroupBase, UserGroupForId
from schemas.auth.UserSchema import UserBase, UserForId
from services.auth.ErrorsService import ErrorsService


class RecordsByID:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def users(self) -> List[UserForId]:
        try:
            users = self.db.query(User).all()
            return {user.id: UserBase(**jsonable_encoder(user)) for user in users}

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def user_groups(self) -> List[UserGroupForId]:
        try:
            groups = self.db.query(UserGroup).all()
            return {
                group.id: UserGroupBase(**jsonable_encoder(group)) for group in groups
            }

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
