from sqlalchemy import Column, Integer, String, UUID, ForeignKey
from database.db import Base
import uuid


class OrganizationOwners(Base):
    """
    Organization owners is a table for Organization Administrators that create their account,
    while there may be more than one organization administrator in an organization, there can be
    only one owner, the one that created the organization when he created his account.
    """
    __tablename__ = "OrganizationOwners"
    uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
    username = Column(String, index = True)
    email = Column(String)
    hashed_password = Column(String)
    organization_name = Column(String)
    hq_address = Column(String)

    def __repr__(self):
        return {
            "uuid": str(self.uuid),
            "username": str(self.username),
            "hashed_password": str(self.hashed_password),
            "organization_name": str(self.organization_name),
            "hq_address": str(self.hq_address)
        }
    
class Organizations(Base):
    """
        This is the table for the organization which will be created at the same time as the Owner.
    """
    __tablename__ = "Organizations"
    link_ref =  Column(String, primary_key=True)
    name = Column(String, index=True)
    owner = Column(UUID, ForeignKey(OrganizationOwners.uuid))
    members = Column(UUID)


class Employees(Base):
    __tablename__ = "Employees"
    uuid = Column(UUID, default=uuid.uuid4, primary_key=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    