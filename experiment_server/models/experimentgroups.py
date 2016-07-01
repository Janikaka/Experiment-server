from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base
from sqlalchemy.orm import relationship
from .users_experimentgroups import users_experimentgroups

class ExperimentGroup(Base):
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    configurations = relationship("Configuration", backref="experimentgroup")
    users = relationship("User",
        secondary=users_experimentgroups,
        back_populates="experimentgroups"
    )
