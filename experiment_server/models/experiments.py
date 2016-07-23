from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime
)

from .meta import Base
from sqlalchemy.orm import relationship

class Experiment(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
    size = Column(Integer)

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            if c.name == 'startDatetime' or c.name == 'endDatetime':
                result[c.name] = str(getattr(self, c.name))
            else:
                result[c.name] = getattr(self, c.name)
        return result
