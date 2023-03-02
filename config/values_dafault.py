from datetime import datetime
from models.user.user import user
from models.function.function import function
from config.db import conn
from auth.auth_service import get_password_hash
from utils.password_generate import password_generate

def user_root():
    root = conn.execute(user.select().where(user.c.id == 1)).first()
    
    if not root:
        userRoot = {    
                        'email': 'root@root.com',
                        'name': "root",
                        'register_date': datetime.now(),
                        'last_login': datetime.now(),
                        'status': 'active'
        }
        password = password_generate(10)
        userRoot['password_hash'] = get_password_hash(password)

        conn.execute(user.insert().values(userRoot))

        print('Root user created, please save the credentials, they will not be shown later')
        print({
            "email": userRoot['email'],
            "password": password
        })
        
def functions_default():
    are_added = conn.execute(function.select().where(function.c.id == 1)).first()
    
    if not are_added:
        fun_list = [
            'Get Users',
            'Get User',
            'Edit User',
            'Create User',
            'User Disable',
            'User Enable',
            'Update Permissions User',
            'Get User Group List',
            'Get User Group',
            'Update User Group',
            'Create User Group',
            'Disable User Group',
            'Enable User Group',
            'Update Permissions Group',
            'Get User Permissions',
            'Group Permissions Available',
            'User Permissions Available',
            'Update User Permission',
            'Create User Permission',
            'Disable Permission',
            'Enable Permission',
            'Update Functions Permission',
            'Get Functions',
            'Functions Available',
            'Get User Permissions Groups',
            'Get Permissions Functions'

        ]

        for fun in fun_list:
            conn.execute(function.insert().values(name=fun))