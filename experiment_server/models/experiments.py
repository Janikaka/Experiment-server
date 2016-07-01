from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text
)

from .meta import Base
from sqlalchemy.orm import relationship

class Experiment(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")
