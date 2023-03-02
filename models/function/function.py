from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from config.db import meta, engine

function = Table('function', meta,
                 Column('id', Integer, primary_key=True),
                 Column('name', String(255), nullable=False, unique=True),
                 Column('is_assigned', Boolean, nullable=False, default=False),
                 )

meta.create_all(engine)
