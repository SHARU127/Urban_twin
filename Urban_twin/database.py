from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


DATABASE_URL = "sqlite:///./urban_twin.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})


SessionLocal = sessionmaker (autocommit= False,autoflush=False,bind=engine)

#base works as a blueprint for creating tables
#declarative_base
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    #why get_db, becuase for every api request we need to assign separate db connection,and closing the connection after evry use.