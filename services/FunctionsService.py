from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from config.Database import get_db_connection
from models.Function import Function
from models.PermissionFunction import PermissionFunction

from schemas.FunctionSchema import FunctionBase, FunctionsResponse
from services.ErrorsService import ErrorsService


class FunctionsService:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get(
        self,
        available: bool = None,
        offset: int = 0,
        limit: int = 150,
        search: str = None,
        permission: int = None,
    ) -> FunctionsResponse:
        try:
            query = self.db.query(Function)

            if search is not None:
                query = query.filter(Function.name.ilike(f"%{search}%"))

            if available is not None:
                query = query.filter(Function.is_assigned != available)

            if permission is not None:
                query = query.join(
                    PermissionFunction,
                    PermissionFunction.function_id == Function.id,
                ).filter(PermissionFunction.permission_id == permission)

            total = query.count()
            functions = query.offset(offset).limit(limit).all()

            return FunctionsResponse(
                offset=offset,
                limit=limit,
                total=total,
                data=functions,
            )

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_id(self, id: int) -> FunctionBase:
        try:
            function = self.db.query(Function).filter(Function.id == id).first()

            if not function:
                ErrorsService().not_found(
                    loc="query",
                    label="function",
                    value=id,
                )

            return function

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def set_functions(
        self, permission: int, functions: List[FunctionBase]
    ) -> FunctionsResponse:
        try:
            functions_permission = (
                self.db.query(PermissionFunction)
                .filter(PermissionFunction.permission_id == permission)
                .all()
            )

            for fun in functions:
                add = True
                if len(functions_permission):
                    for fun_permission in functions_permission:
                        if fun.id == fun_permission.function_id:
                            add = False
                            break

                if add:
                    new_function = PermissionFunction(
                        permission_id=permission, function_id=fun.id
                    )
                    function = self.get_id(id=fun.id)
                    function.is_assigned = True
                    self.db.add(new_function)

            for fun_permission in functions_permission:
                remove = True
                if len(functions):
                    for fun in functions:
                        if fun.id == fun_permission.function_id:
                            remove = False
                            break

                if remove:
                    function = self.get_id(id=fun_permission.function_id)
                    function.is_assigned = False
                    self.db.delete(fun_permission)

            self.db.commit()

            return self.get(permission=permission)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
