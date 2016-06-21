from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base

from sqlalchemy.orm import relationship

class ExperimentGroups(Base):
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiments", back_populates="experimentgroups")
