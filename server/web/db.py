from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@postgres/{os.environ['POSTGRES_DB']}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@asynccontextmanager
async def lifespan(app: FastAPI):
    while True:
        try:
            Base.metadata.create_all(engine)
            break
        except Exception:
            pass
    yield


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
