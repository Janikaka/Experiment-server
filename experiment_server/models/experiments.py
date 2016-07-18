from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime
)

from .meta import Base
from sqlalchemy.orm import relationship
import datetime #Remove this later

class Experiment(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True)
    startDatetime = Column(DateTime, default=datetime.datetime.now()) #Remove default later
    endDatetime = Column(DateTime, default=datetime.datetime.now())
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
    size = Column(Integer, default=100) #Remove default later
