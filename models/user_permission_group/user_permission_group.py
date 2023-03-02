from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine
from models.user_group.user_group import user_group
from models.permission.permission import permission
from models.user.user import user

user_permission_group = Table('user_permission_group', meta,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', Integer, ForeignKey(
                                  user.c.id), nullable=True),
                              Column('group_id', Integer, ForeignKey(
                                  user_group.c.id), nullable=True),
                              Column('permission_id', Integer, ForeignKey(
                                  permission.c.id), nullable=False)
                              )

meta.create_all(engine)
