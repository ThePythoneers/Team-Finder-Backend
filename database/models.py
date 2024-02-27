from sqlalchemy import Column, Integer, String, UUID, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from database.db import Base
import uuid


# user_roles = Table('user_roles', Base.metadata,
#     Column('user_id', UUID, ForeignKey('Users.uuid')),
#     Column('role_id', UUID, ForeignKey('Roles.uuid'))
# )

# class Users(Base):
#     """
#     Organization owners is a table for Organization Administrators that create their account,
#     while there may be more than one organization administrator in an organization, there can be
#     only one owner, the one that created the organization when he created his account.
#     """
#     __tablename__ = "Users"
#     uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
#     username = Column(String, index = True)
#     type_ = Column(Enum("employee", "owner", name="account_role"))
#     email = Column(String)
#     hashed_password = Column(String)
#     organization_name = Column(String)
#     hq_address = Column(String)
#     roles = relationship("Roles", secondary="user_roles",back_populates="users")

    
# class Organizations(Base):
#     """
#         This is the table for the organization which will be created at the same time as the Owner.
#     """
#     __tablename__ = "Organizations"
#     link_ref =  Column(String, primary_key=True)
#     name = Column(String, index=True)
#     owner = Column(UUID, ForeignKey(Users.uuid))
#     members = Column(UUID)

# class Roles(Base):
#     """
#         This is a relationship table for Users.
#     """
#     __tablename__ = "Roles"

#     uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
#     username = Column(String, index = True)
#     users = relationship('Users', secondary=user_roles, back_populates='roles')

"""
See db_struct.png for the new database structure.
"""
DepartmentEmployees = Table('DepartmentEmployees', Base.metadata,
     Column('user_id', UUID, ForeignKey('User.id')),
     Column('department_id', UUID, ForeignKey('Department.id'))
)


class User(Base):
    __tablename__ = "User"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    username = Column(String, index = True)
    email = Column(String)
    hashed_password = Column(String)
    organization_id = Column(String)
    skills = Column(ForeignKey("Skill.id"))
    # department

class Organization(Base):
    __tablename__ = "Organization"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    custom_invite_link = Column(String)
    owner_id = Column(ForeignKey(User.id))
    employees = relationship("Users",backref="Organization")
    organization_name = Column(String)
    hq_address = Column(String)
    roles = Column(String)
    custom_team_role = Column(ForeignKey("Custom_role.id"))

class Custom_role(Base):
    __tablename__ = "Custom_role"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    role_name = Column(String)
    employees = Column(ForeignKey("User.id"))

class Skill(Base):
    __tablename__ = "Skill"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    author = Column(ForeignKey("User.id"))
    departments = Column(ForeignKey("Department.id"))

class Department(Base):
    __tablename__ = "Department"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    department_manager = Column(ForeignKey("User.id"))
    employees = relationship("DepartmentEmployees", secondary=DepartmentEmployees, back_populates="department")

class Project(Base):
    __tablename__ = "Project"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    project_name = Column(String)
    project_period = Column(String)
    start_date = Column(String)
    deadline_date = Column(String)
    project_status = Column(String)
    general_description = Column(String)
    technology_stack = Column(String)
    project_manager = Column(ForeignKey("User.id"))
    team_roles = relationship("Custom_role.id", back_populates="team_role")
