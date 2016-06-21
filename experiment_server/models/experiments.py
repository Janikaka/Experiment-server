from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from sqlalchemy.orm import relationship

from .meta import Base


class Experiments(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experimentgroups = relationship("ExperimentGroups", back_populates="experiment")
    dataitems = relationship(
        "DataItems",
        secondary=dataitems_experiments,
        back_populates="experiments")

Index('experiments_index', Experiments.name, unique=True, mysql_length=255)
