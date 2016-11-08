""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship
from .meta import Base
from .users_experimentgroups import users_experimentgroups


class ExperimentGroup(Base):
    """ This is definition of class ExperimentGroup. """
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    configurations = relationship("Configuration", backref="experimentgroup", cascade="delete")
    users = relationship("User",
                         secondary=users_experimentgroups,
                         back_populates="experimentgroups"
                        )

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_total_dataitems(self):
        """ get total dataitems from the specific experiment group """
        count = 0
        for user in self.users:
            count += user.get_total_dataitems_in_experiment(self.experiment_id)
        return count
