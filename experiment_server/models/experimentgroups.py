""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship
from .meta import Base
from .clients_experimentgroups import clients_experimentgroups


class ExperimentGroup(Base):
    """ This is definition of class ExperimentGroup. """
    __tablename__ = 'experimentgroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    configurations = relationship("Configuration", backref="experimentgroup", cascade="delete")
    clients = relationship("Client",
                         secondary=clients_experimentgroups,
                         back_populates="experimentgroups"
                        )

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_total_dataitems(self):
        """
        Get total dataitems from the specific experiment group
        Calls each client to count their total dataitems
        Return: count of total dataitems in ExperimentGroup
        """
        count = 0
        for client in self.clients:
            count += client.get_total_dataitems_in_experiment(self.experiment_id)
        return count
