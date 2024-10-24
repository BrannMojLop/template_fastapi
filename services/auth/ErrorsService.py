import re
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from schemas.auth.ErrorsSchema import ErrorBaseSchema


class ErrorsService(Exception):
    def __init__(self):
        pass

    def unauthorized(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["headers", ""],
                        msg="Insufficient permissions",
                        type="permission_required",
                    )
                )
            ],
        )

    def credentials(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["body", ""],
                        msg="Invalid login",
                        type="credentials",
                    )
                )
            ],
        )

    def credentials_token(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["headers", ""],
                        msg="Could not validate credentials",
                        type="credentials",
                    )
                )
            ],
            headers={"WWW-Authenticate": "Bearer"},
        )

    def password_temp(self):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["headers", ""],
                        msg="Update password is required",
                        type="credentials",
                    )
                )
            ],
            headers={"WWW-Authenticate": "Bearer"},
        )

    def update_token(self):
        raise HTTPException(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["headers", ""],
                        msg="Update token is required",
                        type="credentials",
                    )
                )
            ],
            headers={"WWW-Authenticate": "Bearer"},
        )

    def bad_request(self, value, loc, msg):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=[loc, str(value)],
                        msg=msg,
                        type="bad_request",
                    )
                )
            ],
        )

    def not_found(self, value, label, loc):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=[loc, label],
                        msg=f"Not found {label} {value}",
                        type="not_found",
                    )
                )
            ],
        )

    def duplicate_entry(self, value, label):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["body", label],
                        msg=f"This {label} '{value}' already exists",
                        type="duplicate",
                    )
                )
            ],
        )

    def internal_error(self, error_msg):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=["internal"],
                        msg=error_msg,
                        type="server_error",
                    )
                )
            ],
        )

    def sqlalchemy_error(self, error):
        error_msg = str(error)

        match = re.search(
            r"Duplicate entry '(?P<value_duplicate>.+)' for key '(?P<column>.+)'",
            error_msg,
        )

        if match:
            value = match.group("value_duplicate")
            label = match.group("column")
            self.duplicate_entry(label=label, value=value)

        if "foreign key constraint fails" in error_msg:
            match_foreign_key = re.search(
                r"foreign key constraint fails .*? REFERENCES `(?P<referenced_table>.+?)` \(.*?`(?P<column>.+?)`",
                error_msg,
            )

            referenced_table = match_foreign_key.group("referenced_table")
            column = match_foreign_key.group("column")
            self.bad_request(
                loc="body",
                value=f"table: {referenced_table} - column: {column}",
                msg="ID reference table not found",
            )
