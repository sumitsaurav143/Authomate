from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

DATABASE_URL = "sqlite:///./kyc.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables on startup
def init_db():
    Base.metadata.create_all(bind=engine)