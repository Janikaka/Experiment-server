from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base


class DataItems(Base):
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.id'))
    value = Column(Integer)

