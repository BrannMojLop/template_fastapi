from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine
from models.function.function import function
from models.permission.permission import permission

permission_function = Table('permission_function', meta,
                            Column('id', Integer, primary_key=True),
                            Column('function_id', Integer, ForeignKey(
                                function.c.id), nullable=False),
                            Column('permission_id', Integer, ForeignKey(
                                permission.c.id), nullable=False)
                            )

meta.create_all(engine)
