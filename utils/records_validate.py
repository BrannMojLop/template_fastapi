from fastapi import Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from config.Database import get_db_connection
from models.auth.User import User
from schemas.auth.UserSchema import UserBase
from services.auth.ErrorsService import ErrorsService


class RecordsValiate:
    def __init__(
        self,
        db: Session = Depends(get_db_connection),
    ):
        self.db = db

    def user(
        self, id: int = 0, email: str = "", phone: str = "", username: str = ""
    ) -> UserBase:
        try:
            user = (
                self.db.query(User)
                .filter(
                    or_(
                        User.id == id,
                        User.email == email,
                        User.phone == phone,
                        User.username == username,
                    )
                )
                .first()
            )

            if not user:
                ErrorsService().not_found(
                    loc="body",
                    label="user",
                    value=id if id else email if email else phone,
                )

            return user

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
