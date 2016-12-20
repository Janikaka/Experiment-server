""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base
from .extension_types.sqltypes import JSONType


class Configuration(Base):
    """
    This is definition of class configuration.
    Configurations are settings which are given to Clients participating the Experiment. Configurations are
    ExperimentGroup-specific.
    Key must be equal to existing ConfigurationKey's name in Application, in which Configuration's ExperimentGroup
    belongs to.
    Configurations are validated with ConfigurationKeys, RangeConstraints and ExclusionConstraints
    """
    __tablename__ = 'configurations'
    id = Column(Integer, primary_key=True)
    experimentgroup_id = Column(Integer, ForeignKey('experimentgroups.id'))
    key = Column(Text)
    value = Column(JSONType())

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
