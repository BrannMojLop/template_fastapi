from typing import List, Union
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from models.auth.App import App
from models.auth.AppUser import AppUser
from models.auth.AppViewUser import AppViewUser
from models.auth.View import View
from schemas.auth.AppSchema import (
    AppBase,
    AppDetails,
    AppPost,
    AppsResponse,
)
from services.auth.ErrorsService import ErrorsService
from services.auth.ViewService import ViewService


class AppService:
    def __init__(
        self,
        db: Session = Depends(get_db_connection),
    ):
        self.db = db

    def get(
        self,
        offset: int = 0,
        limit: int = 150,
        active: bool = None,
        user_id: int = None,
        views: bool = False,
    ) -> Union[AppsResponse, List[AppDetails]]:
        try:
            query = self.db.query(App)

            if active is not None:
                query = query.filter(App.is_active == active)

            if user_id is not None:
                query = query.join(
                    AppUser,
                    AppUser.app_id == App.id,
                ).filter(AppUser.user_id == user_id)

            total = query.count()
            apps = query.offset(offset).limit(limit).all()

            if views:
                apps_format = []
                viewService = ViewService(db=self.db)

                for app in apps:
                    app_format = {}

                    views_app = viewService.get(app_id=app.id).data
                    app_format["views"] = views_app
                    app_format["app"] = app

                    apps_format.append(app_format)

                return apps_format

            return AppsResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=apps,
            )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(self, id: int, views: bool = False) -> Union[AppBase, AppDetails]:
        try:
            app = self.db.query(App).filter(App.id == id).first()

            if not app:
                ErrorsService().not_found(
                    loc="query",
                    label="app",
                    value=id,
                )

            if views:
                views_app = (
                    self.db.query(View)
                    .filter(AppViewUser.app_id == id)
                    .join(
                        AppViewUser,
                        AppViewUser.view_id == View.id,
                    )
                    .all()
                )

                return AppDetails(app=app, views=views_app)

            return app

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, app: AppPost) -> AppBase:
        try:
            new_app = App(**app.dict())
            self.db.add(new_app)
            self.db.commit()

            return new_app

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=app.name)

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, app: AppPost) -> AppBase:
        try:
            result = self.get_id(id)

            for key, value in app.dict(exclude_unset=True).items():
                setattr(result, key, value)

            self.db.commit()

            return result

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=app.name)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> AppBase:
        try:
            app = self.db.query(App).filter(App.id == id).first()

            if not app:
                ErrorsService().not_found(
                    loc="query",
                    label="app_id",
                    value=id,
                )

            app.is_active = state
            self.db.commit()

            return app

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def available_user(self, user_id: int) -> AppsResponse:
        try:
            apps_user = self.db.query(AppUser).filter(AppUser.user_id == user_id).all()

            apps = self.get(active=True)

            if len(apps_user):
                apps_available = []

                for app in apps.data:
                    available = True

                    for app_user in apps_user:
                        if app.id == app_user.app_id:
                            available = False
                            break

                    if available:
                        apps_available.append(app)

                return AppsResponse(
                    offset=0,
                    limit=len(apps_available),
                    total=len(apps_available),
                    data=apps_available,
                )

            else:
                return apps

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_user_apps(
        self,
        user_id: int,
        apps: List[AppBase],
    ) -> AppsResponse:
        try:
            apps_user = self.db.query(AppUser).filter(AppUser.user_id == user_id).all()

            for app in apps:
                add = True

                for app_user in apps_user:
                    if app.id == app_user.app_id:
                        add = False
                        break

                if add:
                    new_app = AppUser(user_id=user_id, app_id=app.id)

                    self.db.add(new_app)

            for app_user in apps_user:
                remove = True

                for app in apps:
                    if app.id == app_user.app_id:
                        remove = False
                        break

                if remove:
                    self.db.delete(app_user)

            self.db.commit()

            return self.get(active=True, user_id=user_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
