from sqlalchemy import Column, Integer, String
from database.db import Base


class OrganizationOwners(Base):
    """
    Organization owners is a table for Organization Administrators that create their account,
    while there may be more than one organization administrator in an organization, there can be
    only one owner, the one that created the organization when he created his account.
    """
    __tablename__ = "OrganizationOwners"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    organization_name = Column(String)
    hq_address = Column(String)

    def __repr__(self):
        return {
            "id": str(self.id),
            "username": str(self.username),
            "hashed_password": str(self.hashed_password),
            "organization_name": str(self.organization_name),
            "hq_address": str(self.hq_address)
        }