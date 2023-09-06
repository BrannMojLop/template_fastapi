from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from schemas.ErrorsSchema import ErrorBaseSchema


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

    def bad_request(self, value, loc, msg):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[
                jsonable_encoder(
                    ErrorBaseSchema(
                        loc=[loc, value],
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
