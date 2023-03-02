from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn, session
from models.permission.permission import permission
from models.function.function import function
from models.user.user import user
from models.permission_function.permission_function import permission_function
from models.user_permission_group.user_permission_group import user_permission_group
from schemas.user_permission import User_Permission, Update_User_Permission
from auth.auth_service import verify_permission, validate_access_token

permissions = APIRouter()


@permissions.get('/user_permissions')
async def get_user_permissions(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=15)

        if permission_verify:
            permissions = {
                'active': [],
                'disabled': []
            }

            query = conn.execute(permission.select()).fetchall()

            for i in query:

                permission_result = dict(i)

                functions = session.query(
                    function.c.id,
                    function.c.name
                ).join(permission_function, permission_function.c.function_id == function.c.id
                       ).filter(permission_function.c.permission_id == i.id).all()

                permission_result['functions'] = functions

                if i.is_active:
                    permissions['active'].append(permission_result)
                else:
                    permissions['disabled'].append(permission_result)

            session.close()

            return permissions

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.get('/group_permissions_available/{group_id}')
async def group_permissions_available(group_id, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=16)

        if permission_verify:
            permissions_group = conn.execute(user_permission_group.select()
                                             .where(user_permission_group.c.group_id == group_id)).fetchall()

            permissions = conn.execute(permission.select()
                                       .where(permission.c.is_active)).fetchall()

            if len(permissions_group):
                permissions_avaible = []

                for per in permissions:
                    available = False

                    for fun_permission in permissions_group:
                        if per.id == fun_permission['permission_id']:
                            available = False
                            break
                        available = True

                    if available:
                        permissions_avaible.append(per)

                return permissions_avaible

            else:
                return permissions

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.get('/user_permissions_available/{user_id}')
async def user_permissions_available(user_id, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=17)

        if permission_verify:
            user_current = conn.execute(user.select().where(
                user.c.id == user_id
            )).first()

            permissions_group = conn.execute(user_permission_group.select()
                                             .where(user_permission_group.c.group_id == user_current.user_group)).fetchall()

            permissions_user = conn.execute(user_permission_group.select()
                                            .where(user_permission_group.c.user_id == user_id)).fetchall()
            permissions = conn.execute(permission.select()
                                       .where(permission.c.is_active)).fetchall()

            if len(permissions_user) or len(permissions_group):
                permissions_avaible = []

                for per in permissions:
                    available = True

                    for fun_permission in permissions_user:
                        if per.id == fun_permission['permission_id']:
                            available = False
                            break

                    if available:
                        for per_permission_group in permissions_group:
                            if per.id == per_permission_group['permission_id']:
                                available = False
                                break

                    if available:
                        permissions_avaible.append(per)

                return permissions_avaible

            else:
                return permissions

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.post('/user_permission')
async def create_user_permission(permissionForm: User_Permission, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=19)

        if permission_verify:
            newPermission = {
                'name': permissionForm.name,
                'is_active': True
            }

            result = conn.execute(permission.insert().values(newPermission))

            permissionCreated = conn.execute(permission.select().where(
                permission.c.id == result.lastrowid)).first()

            return permissionCreated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.put('/user_permission')
async def update_user_permission(permissionForm: Update_User_Permission, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=18)

        if permission_verify:
            conn.execute(permission.update().where(
                permission.c.id == permissionForm.id).values(name=permissionForm.name))

            permissionUpdate = conn.execute(permission.select().where(
                permission.c.id == permissionForm.id)).first()

            return permissionUpdate

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.put('/permission_disable/{id}')
async def disable_permission(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=20)

        if permission_verify:
            conn.execute(permission.update().where(
                permission.c.id == id).values(is_active=False))

            functions = conn.execute(permission_function.select()
                                     .where(permission_function.c.permission_id == id)).fetchall()

            for fun in functions:
                conn.execute(function.update().where(
                    function.c.id == fun['function_id']).values(is_assigned=False))

                conn.execute(permission_function.delete(
                    permission_function.c.id == fun['id']))

            permissionUpdate = conn.execute(permission.select().where(
                permission.c.id == id)).first()

            return permissionUpdate

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.put('/permission_enable/{id}')
async def enable_permission(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=21)

        if permission_verify:
            conn.execute(permission.update().where(
                permission.c.id == id).values(is_active=True))

            permissionUpdate = conn.execute(permission.select().where(
                permission.c.id == id)).first()

            return permissionUpdate

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@permissions.put('/update_functions_permission/{id_permission}')
async def update_functions_permission(id_permission: int, functions: list, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=22)

        if permission_verify:

            functions_permission = conn.execute(permission_function.select().where(
                permission_function.c.permission_id == id_permission)).fetchall()

            for fun in functions:
                add = True

                for fun_permission in functions_permission:
                    if fun['id'] == fun_permission['function_id']:
                        add = False
                        break

                if add:
                    conn.execute(permission_function.insert().values({
                        'permission_id': id_permission,
                        'function_id': fun['id']
                    }))
                    conn.execute(function.update().where(
                        function.c.id == fun['id']).values(is_assigned=1))

            for fun_permission in functions_permission:
                remove = True

                for fun in functions:
                    if fun['id'] == fun_permission['function_id']:
                        remove = False
                        break

                if remove:
                    conn.execute(permission_function.delete(
                        permission_function.c.id == fun_permission['id']))
                    conn.execute(function.update().where(
                        function.c.id == fun_permission['function_id']).values(is_assigned=0))

            return JSONResponse(content={"message": "Updated functions..."}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
