"""
main.py is the head of the project in which all routers are included and 
all errors are handled. 
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.schema import MetaData
import uvicorn
import colorama

from auth import authentication
from account import profile
from database.create_roles import create_roles
from database.db import ENGINE, SESSIONLOCAL, Base
from database import models
from custom_roles import croles
from organization import organizations
from roles import role
from departments import department
from skills import skill
from project import projects
from proposals import proposal
from chatgpt_integration import gpt

app = FastAPI()
metadata = MetaData()
metadata.reflect(ENGINE)

DEBUG_RESET_DATABASE_WHEN_STARTING = True


def get_db():
    """
    creates a db session
    """
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()


models.Base.metadata.create_all(bind=ENGINE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(profile.router)
app.include_router(croles.router)
app.include_router(organizations.router)
app.include_router(role.router)
app.include_router(department.router)
app.include_router(skill.router)
app.include_router(projects.router)
app.include_router(proposal.router)
app.include_router(gpt.router)


@app.exception_handler(RequestValidationError)
# pylint: disable=unused-argument
def validation_exception_handler(request: Request, error: RequestValidationError):
    """
    In case of an empty field in a pydantic BaseModel, we don't return the whole
    message.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content="empty non-null field or bad request",
    )


@app.get("/")
def root():
    """
    Root directory
    """
    return "OK"


if __name__ == "__main__":
    if DEBUG_RESET_DATABASE_WHEN_STARTING:
        print(
            f"{colorama.Fore.GREEN}DEBUG: {colorama.Fore.WHITE}   Database reinitialized (if you don't want this set DEBUG_RESET_DATABASE_WHEN_STARTING to False)."
        )
        for tbl in reversed(metadata.sorted_tables):
            tbl.drop(ENGINE)
            tbl.create(ENGINE)
        create_roles()
        print(
            f"{colorama.Fore.GREEN}DETECTED: {colorama.Fore.WHITE} Database reset, created primary roles."
        )

    uvicorn.run(app="main:app", reload=True)
