from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values
from colorama import Fore
import os

env = dotenv_values(".env")

DEBUG_LOCAL_SWITCH = True

if DEBUG_LOCAL_SWITCH:
    SQL_USERNAME = os.environ.get("LOCAL_SQL_USERNAME")
    SQL_PASSWORD = os.environ.get("LOCAL_SQL_PASSWORD")
    SQL_HOSTNAME = os.environ.get("LOCAL_SQL_HOSTNAME")
    SQL_DATABASE_NAME = os.environ.get("LOCAL_SQL_DATABASE_NAME")
else:
    SQL_USERNAME = os.environ.get("AZURE_SQL_USERNAME")
    SQL_PASSWORD = os.environ.get("AZURE_SQL_PASSWORD")
    SQL_HOSTNAME = os.environ.get("AZURE_SQL_HOSTNAME")
    SQL_DATABASE_NAME = os.environ.get("AZURE_SQL_DATABASE_NAME")

# SQLALCHEMY_DATABASE_URL = f"postgresql://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOSTNAME}:5432/{SQL_DATABASE_NAME}"

SQLALCHEMY_DATABASE_URL = URL.create(
    'postgresql',
    username=SQL_USERNAME,
    password=SQL_PASSWORD,
    host=SQL_HOSTNAME,
    database=SQL_DATABASE_NAME,
)



ENGINE = create_engine(SQLALCHEMY_DATABASE_URL)

SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()
