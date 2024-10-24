from config.Database import SessionLocal
from schemas.auth.AppSchema import AppPost
from schemas.auth.UserGroupSchema import UserGroupPost
from schemas.auth.UserSchema import UserPost
from schemas.auth.ViewSchema import ViewPost
from services.auth.AppService import AppService
from services.auth.ErrorsService import ErrorsService
from services.auth.UserGroupService import UserGroupService
from services.auth.UserService import UserService
from services.auth.ViewService import ViewService


def initial_system():
    try:
        userService = UserService(db=SessionLocal)

        if len(userService.get().data) > 0:
            return

        appService = AppService(db=SessionLocal)
        viewService = ViewService(db=SessionLocal)

        app_admin = appService.create(AppPost(name="/admin"))

        views = ["/admin", "/apps", "/views", "/users", "/users/groups", "permissions"]
        views_base = []

        for view in views:
            view_base = viewService.create(ViewPost(name=view))
            views_base.append(view_base)

        viewService.set_app_views(
            app_id=app_admin.id,
            views=views_base,
        )

        group_admin = UserGroupService(db=SessionLocal).create(
            UserGroupPost(name="Admin")
        )

        user_root = userService.create(
            UserPost(
                username="root",
                first_name="root",
                last_name="root",
                user_group=group_admin.id,
            )
        )

        appService.set_user_apps(
            user_id=user_root.id,
            apps=[app_admin],
        )

    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)
