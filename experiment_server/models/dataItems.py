from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base
from sqlalchemy.orm import relationship


class DataItems(Base):
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    #type = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
