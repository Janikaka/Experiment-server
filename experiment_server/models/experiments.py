from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime
)
from .DictionaryCreator import DictionaryCreator
from .meta import Base
from sqlalchemy.orm import relationship

class Experiment(Base,DictionaryCreator):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
    size = Column(Integer)


