""" This is a schema """
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
    """ This is definition of class dataitem """
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