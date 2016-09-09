""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime
)

from sqlalchemy.orm import relationship
from .DictionaryCreator import DictionaryCreator
from .meta import Base

class Experiment(Base, DictionaryCreator):
    """ This is definition of class Experiment. """
    # TODO Too few public methods (1/2)
    __tablename__ = 'experiments'
    # FIXME "id" is an invalid class attribute name
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
    size = Column(Integer)
