from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    DateTime
)

from .meta import Base
from sqlalchemy.orm import relationship

class DataItem(Base):
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(Text)
    value = Column(Integer)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
