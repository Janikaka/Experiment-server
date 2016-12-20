""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import relationship
from .meta import Base


class Application(Base):
    """
    This is definition of class Application.
    Application is the core of Experiment-Server. Application-class represents Application which is under
    experimentation in Experiment-Server-service.
    id: identifies an Application
    name: name of the Application
    apikey: identifier to Application, which is required when Client is accessing via Api
    experimentDistribution: strategy on how Clients are distributed in Experiments
    experiments: Application's experiments
    configurationkeys: ConfigurationKeys which are allowed to be used in experiments
    """
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    apikey = Column(Text, unique=True)
    experiment_distribution = Column(Text)
    experiments = relationship("Experiment", backref="application", cascade="delete")
    configurationkeys = relationship("ConfigurationKey", backref="application", cascade="delete")

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
