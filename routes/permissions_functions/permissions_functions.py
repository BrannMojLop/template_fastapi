from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.permission_function.permission_function import permission_function
from auth.auth_service import verify_permission, validate_access_token

permissions_functions = APIRouter()


@permissions_functions.get('/permissions_functions')
async def get_permissions_functions(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=26)

        if permission_verify:
            return conn.execute(permission_function.select()).fetchall()

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
