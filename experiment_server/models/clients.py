""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from sqlalchemy import and_
from sqlalchemy.orm import relationship
from .meta import Base
from .clients_experimentgroups import clients_experimentgroups


class Client(Base):
    """
    This is definition of class client.
    Client is a class to identify testers in some Application which is under experimentation in Experiment-Server.
    Clientname is defined by application which client is using. With existing Client, tester can send DataItems to
    Experiment-Server-service.
    """
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    clientname = Column(Text, unique=True, index=True)
    dataitems = relationship("DataItem", backref="client", cascade="delete")
    experimentgroups = relationship(
        "ExperimentGroup",
        secondary=clients_experimentgroups,
        back_populates="clients"
    )

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
