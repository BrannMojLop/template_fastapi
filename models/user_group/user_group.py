from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from config.db import meta, engine

user_group = Table('user_group', meta,
                   Column('id', Integer, primary_key=True),
                   Column('name', String(255)),
                   Column('is_active', Boolean, nullable=False)
                   )

meta.create_all(engine)
