"""
main.py is the head of the project in which all routers are included and 
all errors are handled. 
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from auth import authentication
from account import profile
from database.db import ENGINE
from database import models
from custom_roles import croles
from organization import organizations

app = FastAPI()

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
    uvicorn.run(app="main:app", reload=True)
