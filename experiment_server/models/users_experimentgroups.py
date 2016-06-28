from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Table
)

from .meta import Base

Users_Experimentgroups = Table('users_experimentgroups', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('experimentgroup_id', Integer, ForeignKey('experimentgroups.id'))
)