"""
This is a database-schema.
Required to many-to-many relationship between Client and ExperimentGroup
"""
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table
)

from .meta import Base

clients_experimentgroups = Table('clients_experimentgroups', Base.metadata,
                               Column('client_id', Integer, ForeignKey('clients.id')),
                               Column('experimentgroup_id', Integer,
                                      ForeignKey('experimentgroups.id'))
                              )
