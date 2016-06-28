from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base

from sqlalchemy.orm import relationship
from .users_experimentgroups import Users_Experimentgroups

class ExperimentGroups(Base):
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    configuration = relationship("Configurations", uselist=False, backref="experimentgroup", cascade="delete")
    users = relationship(
        "Users",
        secondary=Users_Experimentgroups,
        back_populates="experimentgroups"
    )







