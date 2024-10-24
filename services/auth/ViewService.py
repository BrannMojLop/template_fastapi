from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from config.Database import get_db_connection
from models.auth.AppUser import AppUser
from models.auth.AppViewUser import AppViewUser
from models.auth.View import View
from schemas.auth.ViewSchema import ViewBase, ViewPost, ViewsResponse
from services.auth.ErrorsService import ErrorsService
from services.auth.UserService import UserService
from utils.records_validate import RecordsValiate


class ViewService:
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
        app_id: int = None,
    ) -> ViewsResponse:
        try:
            query = self.db.query(View)

            if active is not None:
                query = query.filter(View.is_active == active)

            if user_id is not None:
                query = query.join(
                    AppViewUser,
                    AppViewUser.view_id == View.id,
                ).filter(AppViewUser.user_id == user_id)

            if app_id is not None:
                query = query.join(
                    AppViewUser,
                    AppViewUser.view_id == View.id,
                ).filter(AppViewUser.app_id == app_id)

            total = query.count()
            views = query.offset(offset).limit(limit).all()

            return ViewsResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=views,
            )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(self, id: int) -> ViewBase:
        try:
            view = self.db.query(View).filter(View.id == id).first()

            if not view:
                ErrorsService().not_found(
                    loc="query",
                    label="view",
                    value=id,
                )

            return view

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def create(self, view: ViewPost) -> ViewBase:
        try:
            new_view = View(**view.dict())
            self.db.add(new_view)
            self.db.commit()

            return new_view

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=view.name)

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def update(self, id: int, view: ViewPost) -> ViewBase:
        try:
            result = self.get_id(id)

            for key, value in view.dict(exclude_unset=True).items():
                setattr(result, key, value)

            self.db.commit()

            return result

        except SQLAlchemyError as e:
            error_msg = str(e)

            if "Duplicate entry" in error_msg:
                ErrorsService().duplicate_entry(label="name", value=view.name)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def on_off(self, id: int, state: bool) -> ViewBase:
        try:
            view = self.db.query(View).filter(View.id == id).first()

            if not view:
                ErrorsService().not_found(
                    loc="query",
                    label="view_id",
                    value=id,
                )

            view.is_active = state
            self.db.commit()

            return view

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def available_app(self, app_id: int) -> ViewsResponse:
        try:
            views_app = (
                self.db.query(AppViewUser).filter(AppViewUser.app_id == app_id).all()
            )

            views = self.get(active=True)

            if len(views_app):
                views_avaible = []

                for view in views.data:
                    available = True

                    for view_app in views_app:
                        if view.id == view_app.view_id:
                            available = False
                            break

                    if available:
                        views_avaible.append(view)

                return ViewsResponse(
                    offset=0,
                    limit=len(views_avaible),
                    total=len(views_avaible),
                    data=views_avaible,
                )

            else:
                return views

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def available_user(self, user_id: int) -> ViewsResponse:
        try:
            recordsValiate = RecordsValiate(db=self.db)
            recordsValiate.user(user_id)

            views_user = (
                self.db.query(AppViewUser).filter(AppViewUser.user_id == user_id).all()
            )

            apps_user = self.db.query(AppUser).filter(AppUser.user_id == user_id).all()

            views_apps = []

            for app in apps_user:
                view_app = (
                    self.db.query(AppViewUser)
                    .filter(AppViewUser.app_id == app.id)
                    .all()
                )

                views_apps += view_app

            views = self.get(active=True)

            if len(views_apps) or len(views_user):
                views_avaible = []

                for view in views.data:
                    available = True

                    for view_user in views_user:
                        if view.id == view_user.view_id:
                            available = False
                            break

                    if available:
                        for view_app in views_apps:
                            if view.id == view_app.view_id:
                                available = False
                                break

                    if available:
                        views_avaible.append(view)

                return ViewsResponse(
                    offset=0,
                    limit=len(views_avaible),
                    total=len(views_avaible),
                    data=views_avaible,
                )

            else:
                return views

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_user_views(
        self,
        user_id: int,
        views: List[ViewBase],
    ) -> ViewsResponse:
        try:
            views_user = (
                self.db.query(AppViewUser).filter(AppViewUser.user_id == user_id).all()
            )

            for view in views:
                add = True

                for view_user in views_user:
                    if view.id == view_user.view_id:
                        add = False
                        break

                if add:
                    new_view = AppViewUser(user_id=user_id, view_id=view.id)

                    self.db.add(new_view)

            for view_user in views_user:
                remove = True

                for view in views:
                    if view.id == view_user.view_id:
                        remove = False
                        break

                if remove:
                    self.db.delete(view_user)

            UserService(db=self.db).next_access_version(id=user_id)
            self.db.commit()

            return self.get(active=True, user_id=user_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_app_views(
        self,
        app_id: int,
        views: List[ViewBase],
    ) -> ViewsResponse:
        try:
            views_app = (
                self.db.query(AppViewUser).filter(AppViewUser.app_id == app_id).all()
            )

            for view in views:
                add = True
                if len(views_app):
                    for view_app in views_app:
                        if view.id == view_app.view_id:
                            add = False
                            break

                if add:
                    new_view = AppViewUser(app_id=app_id, view_id=view.id)
                    self.db.add(new_view)

            for view_app in views_app:
                remove = True
                if len(views):
                    for view in views:
                        if view.id == view_app.view_id:
                            remove = False
                            break

                if remove:
                    self.db.delete(view_app)

            users_app = self.db.query(AppUser).filter(AppUser.app_id == app_id).all()

            for record in users_app:
                UserService(db=self.db).next_access_version(id=record.user_id)

            self.db.commit()

            return self.get(active=True, app_id=app_id)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
