from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

SQL_USERNAME = "postgres"
SQL_PASSWORD = "123"
SQL_HOSTNAME = "127.0.0.1"
SQL_DATABASE_NAME = "team_app"

SQLALCHEMY_DATABASE_URL = f"postgresql://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOSTNAME}:5432/{SQL_DATABASE_NAME}"

ENGINE = create_engine(SQLALCHEMY_DATABASE_URL)

SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()
