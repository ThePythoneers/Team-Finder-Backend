"""
    Tool to automatically create roles.
    Must replace import database.db -> import db in models.py to work
"""

from models import Primary_Roles
from db import SESSIONLOCAL


session = SESSIONLOCAL()

user_roles = ["Employee", "Organization Admin", "Department Manager", "Project Manager"]
for role in user_roles:
    new_role = Primary_Roles(role_name=role)
    session.add(new_role)

session.commit()
