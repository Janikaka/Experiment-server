""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    PickleType
)

from .meta import Base


class Configuration(Base):
    """ This is definition of class configuration """
    __tablename__ = 'configurations'
    id = Column(Integer, primary_key=True)
    experimentgroup_id = Column(Integer, ForeignKey('experimentgroups.id'))
    key = Column(Text)
    value = Column(PickleType)

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns} # col.name means data from column
