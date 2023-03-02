from sqlalchemy import create_engine, MetaData
from utils.settings import Settings
from sqlalchemy.orm import Session

settings = Settings()

DATABASE = settings.db_name
PASSWORD= settings.db_password
HOST= settings.db_host
USERNAME_DB= settings.db_username
PORT = settings.db_port

URI = 'mysql+pymysql://' + USERNAME_DB + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DATABASE

engine = create_engine(URI)

meta = MetaData()

conn = engine.connect()

session = Session(engine)