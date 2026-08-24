from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

#synchronous
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#tracking of table definitions
class Base(DeclarativeBase):
    pass


#dependancy generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()