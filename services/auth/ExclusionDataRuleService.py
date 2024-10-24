from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from config.Database import get_db_connection
from models.auth.ExclusionDataRule import ExclusionDataRule
from services.auth.ErrorsService import ErrorsService


class ExclusionDataRuleService:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get_data_exclused(self, user: int, table: str):
        try:
            query_to_exclude = (
                self.db.query(ExclusionDataRule)
                .filter(ExclusionDataRule.table == table)
                .filter(ExclusionDataRule.user == user)
                .filter(ExclusionDataRule.action == None)
                .all()
            )

            columns_to_exclude = [
                field.value for field in query_to_exclude if field.value is not None
            ]

            records_to_exclude = [
                field.record for field in query_to_exclude if field.record is not None
            ]

            return {"columns": columns_to_exclude, "records": records_to_exclude}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)

    def get_exclused_actions(self, user: int, table: str, action: str):
        try:
            return (
                self.db.query(ExclusionDataRule)
                .filter(ExclusionDataRule.table == table)
                .filter(ExclusionDataRule.user == user)
                .filter(ExclusionDataRule.action == action)
                .all()
            )

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            error_msg = str(e)
            ErrorsService().internal_error(error_msg)
