from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base


class ExperimentGroups(Base):
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    experiment = Column(Integer, ForeignKey('experiments.id'))
    name = Column(Text)