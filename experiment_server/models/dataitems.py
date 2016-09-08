from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    PickleType
)
from .meta import Base
from .DictionaryCreator import DictionaryCreator


class DataItem(Base, DictionaryCreator):
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(Text)
    value = Column(PickleType)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
