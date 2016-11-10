""" This is a schema """
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
