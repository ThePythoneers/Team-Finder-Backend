from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.orm import Session
import uvicorn

from auth import authentication
from account import profile
from database.db import ENGINE, SESSIONLOCAL
from database import models

app = FastAPI()

models.Base.metadata.create_all(bind=ENGINE)


def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

user_roles = ["Employee","Organization Admin","Department Manager", "Project Manager"]
db_dependency = Annotated[Session, Depends(get_db)]



@app.get("/")
def root():
    return "OK"

app.include_router(authentication.router)
app.include_router(profile.router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)