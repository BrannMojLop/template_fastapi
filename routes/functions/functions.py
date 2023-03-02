from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.function.function import function
from models.permission_function.permission_function import permission_function
from auth.auth_service import verify_permission, validate_access_token

functions = APIRouter()


@functions.get('/functions')
async def get_functions(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=23)

        if permission_verify:
            return conn.execute(function.select()).fetchall()
        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@functions.get('/functions_available/{permission_id}')
async def functions_available(permission_id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=24)

        if permission_verify:
            functions_permission = conn.execute(permission_function.select()
                                                .where(permission_function.c.permission_id == permission_id)).fetchall()

            functions_query = conn.execute(function.select()
                                           .where(function.c.is_assigned == False)).fetchall()

            if len(functions_permission):
                availables = []

                for fun in functions_query:
                    available = False

                    for fun_permission in functions_permission:
                        if fun.id == fun_permission['function_id']:
                            available = False
                            break
                        available = True

                    if available:
                        availables.append(fun)

                return availables

            else:
                return functions_query

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
