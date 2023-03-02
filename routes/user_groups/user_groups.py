from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn, session
from models.user_group.user_group import user_group
from models.user_permission_group.user_permission_group import user_permission_group
from models.permission.permission import permission
from schemas.user_group import User_Group, Update_User_Group
from auth.auth_service import verify_permission, validate_access_token


user_groups = APIRouter()


@user_groups.get('/user_groups_list')
async def get_user_group_list(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=8)

        if permission_verify:

            return conn.execute(user_group.select().where(user_group.c.is_active)).fetchall()

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.get('/user_groups')
async def get_user_group(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=9)

        if permission_verify:
            users_groups = {
                'active': [],
                'disabled': []
            }

            query = conn.execute(user_group.select()).fetchall()

            for gruop in query:

                group_result = dict(gruop)

                permissions = session.query(
                    permission.c.id,
                    permission.c.name
                ).join(user_permission_group, user_permission_group.c.permission_id == permission.c.id
                       ).filter(user_permission_group.c.group_id == gruop.id).filter(
                           permission.c.is_active).all()

                group_result['permissions'] = permissions

                if gruop.is_active:
                    users_groups['active'].append(group_result)
                else:
                    users_groups['disabled'].append(group_result)

            session.close()

            return users_groups

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.post('/user_group')
async def create_user_group(groupForm: User_Group, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=11)

        if permission_verify:
            newGroup = {
                'name': groupForm.name,
                'is_active': True
            }

            result = conn.execute(user_group.insert().values(newGroup))
            groupCreated = conn.execute(user_group.select().where(
                user_group.c.id == result.lastrowid)).first()

            return groupCreated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.put('/user_group')
async def update_user_group(groupForm: Update_User_Group, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=10)

        if permission_verify:
            conn.execute(user_group.update().where(
                user_group.c.id == groupForm.id).values(name=groupForm.name))

            groupUpdated = conn.execute(user_group.select().where(
                user_group.c.id == groupForm.id)).first()

            return groupUpdated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.put('/user_group_disable/{id}')
async def disable_user_group(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=12)

        if permission_verify:
            conn.execute(user_group.update().where(
                user_group.c.id == id).values(is_active=False))

            groupUpdated = conn.execute(user_group.select().where(
                user_group.c.id == id)).first()

            return groupUpdated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.put('/user_group_enable/{id}')
async def enable_user_group(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=13)

        if permission_verify:
            conn.execute(user_group.update().where(
                user_group.c.id == id).values(is_active=True))

            groupUpdated = conn.execute(user_group.select().where(
                user_group.c.id == id)).first()

            return groupUpdated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@user_groups.put('/update_permissions_group/{id_group}')
async def update_permissions_group(id_group: int, permissions: list, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=14)

        if permission_verify:

            permissions_group = conn.execute(user_permission_group.select().where(
                user_permission_group.c.group_id == id_group)).fetchall()

            for per in permissions:
                add = True
                if len(permissions_group):

                    for per_group in permissions_group:
                        if per['id'] == per_group['permission_id']:
                            add = False
                            break
                        else:
                            add = True

                if add:
                    conn.execute(user_permission_group.insert().values({
                        'group_id': id_group,
                        'permission_id': per['id']
                    }))

            for per_group in permissions_group:
                remove = False

                if len(permissions_group):
                    if len(permissions):

                        for per in permissions:
                            if per['id'] == per_group['permission_id']:
                                remove = False
                                break
                            else:
                                remove = True
                    else:
                        remove = True

                if remove:
                    conn.execute(user_permission_group.delete(
                        user_permission_group.c.id == per_group['id']))

            return JSONResponse(content={"message": "Updated permissions..."}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
