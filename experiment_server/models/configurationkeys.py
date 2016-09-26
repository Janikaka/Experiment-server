""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from .meta import Base


class ConfigurationKey(Base):
    """ This is definition of Configurationkey class """
    __tablename__ = 'configurationkeys'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(Text)
    type = Column(Text)
    rangeconstraints = relationship("RangeConstraint", backref="configurationkey", cascade="delete")

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
