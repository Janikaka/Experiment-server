""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime
)
from .meta import Base
from .dictionary_creator import DictionaryCreator
from .extension_types.sqltypes import JSONType


class DataItem(Base, DictionaryCreator):
    """ This is definition of class dataitem """
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(Text)
    value = Column(JSONType())
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}