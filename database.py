from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass


database_url = "sqlite:///users.db"

engine = create_engine(database_url)

session_local = sessionmaker(bind=engine)