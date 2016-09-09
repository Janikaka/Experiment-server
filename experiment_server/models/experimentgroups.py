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
    # TODO Too few public methods (1/2)
    __tablename__ = 'experimentgroups'
    # FIXME "id" is an invalid class attribute name
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
