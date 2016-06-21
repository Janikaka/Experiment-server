from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Table
)

from .meta import Base
from sqlalchemy.orm import relationship

dataitems_experiments = Table('dataitems_experiments', Base.metadata,
    Column('left_id', Integer, ForeignKey('dataitems.id')),
    Column('right_id', Integer, ForeignKey('experiments.id'))
)
"""
class DataItems(Base):
    __tablename__ = 'dataitems'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users", back_populates="dataitems")
    experiments = relationship(
        "Experiments",
        secondary=dataitems_experiments,
        back_populates="dataitems")


class Experiments(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experimentgroups = relationship("ExperimentGroups", back_populates="experiment")
    dataitems = relationship(
        "DataItems",
        secondary=dataitems_experiments,
        back_populates="experiments")

Index('experiments_index', Experiments.name, unique=True, mysql_length=255)"""

