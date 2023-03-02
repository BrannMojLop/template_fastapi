from fastapi import APIRouter, Depends
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn, session
from models.user.user import user
from models.user_group.user_group import user_group
from models.user_permission_group.user_permission_group import user_permission_group
from models.permission.permission import permission
from schemas.user import User, User_Login, User_Validation, UserUpdate, User_Reset_Password
from auth.auth_service import get_password_hash, verify_password, verify_user, create_access_token, verify_permission, validate_access_token, validate_email
from jobs.emails.verify_account import send_email
from jobs.emails.reset_password import reset_password
from utils.password_generate import password_generate

users_records = APIRouter()


@users_records.get('/users')
async def get_users(current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=1)

        if permission_verify:
            users = {
                'active': [],
                'disabled': []
            }

            result = session.query(
                user.c.id,
                user.c.email,
                user.c.phone,
                user.c.name,
                user.c.last_name_first,
                user.c.last_name_second,
                user.c.user_group,
                user.c.register_date,
                user.c.status,
                user.c.last_login,
                user_group.c.name.label('user_group_name'),
            ).join(user_group, isouter=True).filter(user.c.id != current_user['data'][0]['id']).all()

            filters = {
                'user_group': [],
                'status': [],
            }

            for i in result:

                user_result = dict(i)

                permissions = session.query(
                    permission.c.id,
                    permission.c.name
                ).join(user_permission_group, user_permission_group.c.permission_id == permission.c.id
                       ).filter(user_permission_group.c.user_id == i.id).filter(
                           permission.c.is_active).all()

                user_result['permissions'] = permissions

                if i['status'] == 'disabled':
                    users['disabled'].append(user_result)

                else:
                    users['active'].append(user_result)

                if i['user_group']:
                    if not i['user_group_name'] in filters['user_group']:
                        filters['user_group'].append(i['user_group_name'])

                if i['status'] != 'disabled':
                    if not i['status'] in filters['status']:
                        filters['status'].append(i['status'])

            session.close()

            return {
                'users': users,
                'filters': filters
            }

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.get('/user/{id}')
async def get_user(id: str, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=2)

        if permission_verify:
            return conn.execute(user.select().where(user.c.id == id)).first()

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.post('/user')
async def create_user(userForm: User, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=4)

        if permission_verify:
            newUser = {
                'email': userForm.email,
                'phone': userForm.phone,
                'name': userForm.name,
                'last_name_first': userForm.last_name_first,
                'last_name_second': userForm.last_name_second,
                'user_group': userForm.user_group,
                'register_date': datetime.now(),
                'last_login': datetime.now(),
                'status': 'validation'
            }

            newUser['password_hash'] = get_password_hash(password_generate(10))

            result = conn.execute(user.insert().values(newUser))

            userCreated = conn.execute(user.select().where(
                user.c.id == result.lastrowid)).first()

            access_token = create_access_token(userCreated, 'user_platform')

            await send_email([userCreated.email], access_token['access_token'], 'user_platform')

            return userCreated

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.put('/user/{id}')
async def edit_user(id: int, userForm: UserUpdate, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=3)

        if permission_verify:
            updateUser = {
                'email': userForm.email,
                'phone': userForm.phone,
                'name': userForm.name,
                'last_name_first': userForm.last_name_first,
                'last_name_second': userForm.last_name_second,
                'user_group': userForm.user_group
            }

            conn.execute(user.update().where(
                user.c.id == id).values(updateUser))

            userEdited = conn.execute(user.select().where(
                user.c.id == id)).first()

            return userEdited

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.post('/user/verification_resend/{email}')
async def user_verification_resend(email: str, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=48)

        if permission_verify:
            user_current = verify_user(email)

            if user_current:
                access_token = create_access_token(user_current, 'user_platform')
                await send_email([email], access_token['access_token'], 'user_platform')

                return JSONResponse(content={"message": "Email Sent"}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.post('/user/send_reset_password/{email}')
async def user_reset_password(email: str):
    try:
        user_current = verify_user(email)

        if user_current:
            access_token = create_access_token(user_current, 'user_platform')
            await reset_password([email], access_token['access_token'], 'user_platform')

            return JSONResponse(content={"message": "Email Sent"}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.post('/user/reset_password')
async def reset_password(formResetPassword: User_Reset_Password):
    try:
        user_current = await validate_access_token(formResetPassword.access_token)

        password_hash = get_password_hash(formResetPassword.password)

        conn.execute(user_current.update().where(
            user.c.id == user_current['data'][0]['id']).values(password_hash=password_hash))

        return JSONResponse(content={"message": "Action completed"}, status_code=200)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.post('/user/verification')
async def verification_account_user(validationForm: User_Validation):
    access_token = await validate_email(validationForm.token)

    if access_token:

        password = get_password_hash(validationForm.password)

        conn.execute(user.update().where().values({
            'status': 'active',
            'password_hash': password
        }))

        user_current = conn.execute(user.select().where(
            user.c.id == access_token['id'])).first()

        access_token = create_access_token(user_current, 'user_platform')

        return access_token

    else:
        return JSONResponse(
            content={"message": "Token expired"}, status_code=400)


@users_records.post('/user/login')
def user_login(user_login: User_Login):
    user_current = verify_user(user_login.email)
    if user_current:
        if verify_password(user_login.password, user_current.password_hash):
            access_token = create_access_token(user_current, 'user_platform')
            conn.execute(user.update().where(
                user.c.id == user_current.id).values(last_login=datetime.now()))
            return access_token
        else:
            return JSONResponse(content={"message": "Invalid login"}, status_code=401)
    else:
        return JSONResponse(content={"message": "Invalid login"}, status_code=401)


@users_records.put('/user/disable/{id}')
async def user_disable(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=5)

        if permission_verify:

            conn.execute(user.update().where(
                user.c.id == id).values(status='disabled'))

            return JSONResponse(content={"message": "User disabled"}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.put('/user/enable/{id}')
async def user_enable(id: int, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=6)

        if permission_verify:

            conn.execute(user.update().where(
                user.c.id == id).values(status='active'))

            return JSONResponse(content={"message": "User Enable"}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error


@users_records.put('/update_permissions_user/{id_user}')
async def update_permissions_user(id_user: int, permissions: list, current_user=Depends(validate_access_token)):
    try:
        permission_verify = await verify_permission(current_user['data'][0], function=7)

        if permission_verify:

            permissions_user = conn.execute(user_permission_group.select().where(
                user_permission_group.c.user_id == id_user)).fetchall()

            for per in permissions:
                add = True
                if len(permissions_user):

                    for per_user in permissions_user:
                        if per['id'] == per_user['permission_id']:
                            add = False
                            break
                        else:
                            add = True

                if add:
                    conn.execute(user_permission_group.insert().values({
                        'user_id': id_user,
                        'permission_id': per['id']
                    }))

            for per_user in permissions_user:
                remove = False

                if len(permissions_user):
                    if len(permissions):

                        for per in permissions:
                            if per['id'] == per_user['permission_id']:
                                remove = False
                                break
                            else:
                                remove = True
                    else:
                        remove = True

                if remove:
                    conn.execute(user_permission_group.delete(
                        user_permission_group.c.id == per_user['id']))

            return JSONResponse(content={"message": "Updated permissions..."}, status_code=200)

        else:
            return JSONResponse(content={"message": "Insufficient permissions"}, status_code=401)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
