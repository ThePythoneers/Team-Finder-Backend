from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values
from colorama import Fore

env = dotenv_values(".env")

DEBUG_LOCAL_SWITCH = False

if DEBUG_LOCAL_SWITCH:
    SQL_USERNAME = env["LOCAL_SQL_USERNAME"]
    SQL_PASSWORD = env["LOCAL_SQL_PASSWORD"]
    SQL_HOSTNAME = env["LOCAL_SQL_HOSTNAME"]
    SQL_DATABASE_NAME = env["LOCAL_SQL_DATABASE_NAME"]
else:
    SQL_USERNAME = env["AZURE_SQL_USERNAME"]
    SQL_PASSWORD = env["AZURE_SQL_PASSWORD"]
    SQL_HOSTNAME = env["AZURE_SQL_HOSTNAME"]
    SQL_DATABASE_NAME = env["AZURE_SQL_DATABASE_NAME"]

SQLALCHEMY_DATABASE_URL = f"postgresql://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOSTNAME}:5432/{SQL_DATABASE_NAME}"

ENGINE = create_engine(SQLALCHEMY_DATABASE_URL)

SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()
