from pydantic import BaseModel

class RegisterOwner(BaseModel):
    username: str
    email: str
    password: str
    organization_name: str
    hq_address: str

class RegisterEmployee(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict