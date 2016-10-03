""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime
)

from sqlalchemy.orm import relationship
from experiment_server.models.dictionary_creator import DictionaryCreator
from experiment_server.models.meta import Base

class Experiment(Base, DictionaryCreator):
    """ This is definition of class Experiment. """
    # TODO Too few public methods (1/2)
    __tablename__ = 'experiments'
    # FIXME "id" is an invalid class attribute name
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(Text, unique=True, index=True)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
    size = Column(Integer)