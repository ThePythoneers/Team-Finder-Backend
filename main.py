from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware 
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import uvicorn

from auth import authentication
from account import profile
from database.db import ENGINE, SESSIONLOCAL
from database import models
from custom_roles import croles
from organization import organizations


app = FastAPI()

models.Base.metadata.create_all(bind=ENGINE)


def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

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
def validation_exception_handler(request: Request, error: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content = "empty non-null field or bad request"
    )


@app.get("/")
def root():
    return "OK"

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)