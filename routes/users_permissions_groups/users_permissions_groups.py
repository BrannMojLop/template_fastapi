from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.user_permission_group.user_permission_group import user_permission_group
from auth.auth_service import verify_permission, validate_access_token


users_permissions_groups = APIRouter()


@users_permissions_groups.get('/users_permissions_groups')
async def get_user_permissions_groups(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=25)

        if permission_verify:
            return conn.execute(user_permission_group.select()).fetchall()
        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
