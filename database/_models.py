from sqlalchemy import Column, Integer, String, UUID, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from database.db import Base
import uuid




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
# DepartmentEmployees = Table('DepartmentEmployees', Base.metadata,
#      Column('user_id', UUID, ForeignKey('TUser.id')),
#      Column('department_id', UUID, ForeignKey('TDepartment.id'))
# )
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', UUID, ForeignKey('Users.id')),
    Column('role_id', UUID, ForeignKey('Custom_roles.id'))
)

class User(Base):
    __tablename__ = "TUser"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    username = Column(String, index = True)
    email = Column(String)
    hashed_password = Column(String)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("TOrganization.id"))
    organization = relationship("Organization", back_populates="employees")
    # skills = Column(ForeignKey("TSkill.id"))
    #adresa se inregistreaza direct in organization chiar daca se face deodata cu inregistrarea
    # department

class Organization(Base):
    __tablename__ = "TOrganization"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    custom_invite_link = Column(String)
    owner_id = Column(UUID)
    organization_name = Column(String)
    hq_address = Column(String)
    employees = relationship("User", back_populates="organization")
    # custom_team_role = Column(ForeignKey("TCustom_role.id"))

class Custom_role(Base):
    __tablename__ = "TCustom_role"
    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    organization_id = Column(String)
    role_name = Column(String)
    employees = Column(ForeignKey("TUser.id"))

# class Skill(Base):
#     __tablename__ = "TSkill"
#     id = Column(UUID, default=uuid.uuid4, primary_key=True)
#     name = Column(String)
#     category = Column(String)
#     description = Column(String)
#     author = Column(ForeignKey("TUser.id"))
#     departments = Column(ForeignKey("TDepartment.id"))

# class Department(Base):
#     __tablename__ = "TDepartment"
#     id = Column(UUID, default=uuid.uuid4, primary_key=True)
#     department_manager = Column(ForeignKey("TUser.id"))
#     employees = relationship("User", secondary=DepartmentEmployees, back_populates="department")

# class Project(Base):
#     __tablename__ = "TProject"
#     id = Column(UUID, default=uuid.uuid4, primary_key=True)
#     project_name = Column(String)
#     project_period = Column(String)
#     start_date = Column(String)
#     deadline_date = Column(String)
#     project_status = Column(String)
#     general_description = Column(String)
#     technology_stack = Column(String)
#     project_manager = Column(ForeignKey("TUser.id"))
#     team_roles = relationship("Custom_role.id", back_populates="team_role")
