from models.User import User
from models.Function import Function
from config.Database import SessionLocal
from services.ErrorsService import ErrorsService
from utils.password_generate import password_generate
from services.AuthService import AuthService


def initial_system():
    try:
        # User root
        root = SessionLocal.query(User).count()

        if root == 0:
            new_user = {
                "id": 1,
                "name": "root",
                "last_name_first": "root",
                "last_name_second": "root",
                "type": "root",
            }

            authService = AuthService(**new_user)
            new_password = password_generate(8)
            password_hash = authService.get_password_hash(new_password)

            new_user["password_hash"] = password_hash

            add_user = User(**new_user)

            SessionLocal.add(add_user)

            print(
                "Root user created, please save the credentials, they will not be shown later"
            )

            print({"user": "root", "password": new_password})

            # Functions default
            fun_list = [
                "Get Users",
                "Get User",
                "Edit User",
                "Create User",
                "User Disable",
                "User Enable",
                "Update Permissions User",
                "Get User Group List",
                "Get User Group",
                "Update User Group",
                "Create User Group",
                "Disable User Group",
                "Enable User Group",
                "Update Permissions Group",
                "Get User Permissions",
                "Group Permissions Available",
                "User Permissions Available",
                "Update User Permission",
                "Create User Permission",
                "Disable Permission",
                "Enable Permission",
                "Update Functions Permission",
                "Get Functions",
                "Functions Available",
                "Get User Permissions Groups",
                "Get Permissions Functions",
            ]
            for fun in fun_list:
                new_function = Function(name=fun)
                SessionLocal.add(new_function)

            SessionLocal.commit()

    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)

    finally:
        SessionLocal.close()
