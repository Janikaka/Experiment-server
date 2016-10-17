""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime
)

from sqlalchemy.orm import relationship
from experiment_server.models.meta import Base

class Experiment(Base):
    """ This is definition of class Experiment. """
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
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