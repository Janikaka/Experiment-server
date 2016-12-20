""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime
)
from .meta import Base
from .extension_types.sqltypes import JSONType


class DataItem(Base):
    """
    This is definition of class DataItem.
    DataItem holds Experiments' data given by the Clients, who have been using Application which is being tested. Be
    very careful not to delete DataItems accidentally, since they might hold important data to the user.
    This Experiment-Server does not intervene to the contents of Key and Value. They are on users' responsibility.
    """
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    key = Column(Text)
    value = Column(JSONType())
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)

    def as_dict(self):
        """ Transfer data to dictionary """
        result = {}
        for c in self.__table__.columns:
            if c.name == 'startDatetime' or c.name == 'endDatetime':
                result[c.name] = str(getattr(self, c.name))
            else:
                result[c.name] = getattr(self, c.name)
        return result