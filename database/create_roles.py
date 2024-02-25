from models import Roles
from sqlalchemy.orm import Session
from db import SESSIONLOCAL

"""
    Tool to automatically create roles.
    Must replace import database.db -> import db in models.py to work
"""


session = SESSIONLOCAL()

user_roles = ["Employee","Organization Admin","Department Manager", "Project Manager"]
for role in user_roles:
    new_role = Roles(username=role)
    session.add(new_role)

session.commit()
