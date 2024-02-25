from sqlalchemy import Column, Integer, String, UUID, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from database.db import Base
import uuid


user_roles = Table('user_roles', Base.metadata,
    Column('user_id', UUID, ForeignKey('Users.uuid')),
    Column('role_id', UUID, ForeignKey('Roles.uuid'))
)

class Users(Base):
    """
    Organization owners is a table for Organization Administrators that create their account,
    while there may be more than one organization administrator in an organization, there can be
    only one owner, the one that created the organization when he created his account.
    """
    __tablename__ = "Users"
    uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
    username = Column(String, index = True)
    type_ = Column(Enum("employee", "owner", name="account_role"))
    email = Column(String)
    hashed_password = Column(String)
    organization_name = Column(String)
    hq_address = Column(String)
    roles = relationship("Roles", secondary="user_roles",back_populates="users")

    
class Organizations(Base):
    """
        This is the table for the organization which will be created at the same time as the Owner.
    """
    __tablename__ = "Organizations"
    link_ref =  Column(String, primary_key=True)
    name = Column(String, index=True)
    owner = Column(UUID, ForeignKey(Users.uuid))
    members = Column(UUID)

class Roles(Base):
    """
        This is a relationship table for Users.
    """
    __tablename__ = "Roles"

    uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
    username = Column(String, index = True)
    users = relationship('Users', secondary=user_roles, back_populates='roles')

