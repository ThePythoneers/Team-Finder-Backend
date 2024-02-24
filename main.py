from fastapi import FastAPI
import uvicorn

from auth.authentication import router
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

@app.get("/")
def root():
    return "OK"

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)