from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from config.db import meta, engine
from models.user_group.user_group import user_group

user = Table('user', meta,
                    Column('id', Integer, primary_key=True),
                    Column('name', String(255)),
                    Column('last_name_first', String(255)),
                    Column('last_name_second', String(255)),
                    Column('email', String(255), unique=True),
                    Column('password_hash', String(255)),
                    Column('phone', String(25), unique=True),
                    Column('register_date', DateTime, nullable=False),
                    Column('last_login', DateTime, nullable=False),
                    Column('status', String(255), nullable=False),
                    Column('user_group', Integer, ForeignKey(
                        user_group.c.id), nullable=True),
                    )

meta.create_all(engine)
