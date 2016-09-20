""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    PickleType
)

from sqlalchemy.orm import relationship
from .meta import Base


class Constraint(Base):
    """ This is definition of class Constraints """
    __tablename__ = 'constraints'
    id = Column(Integer, primary_key=True)
    main_configuration_id = Column(Integer, ForeignKey('configurations.id'))
    configuration_id = Column(Integer, ForeignKey('configurations.id'))
    value = Column(PickleType)

    main_configuration = relationship("Configuration", foreign_keys=[main_configuration_id])
    configuration = relationship("Configuration", foreign_keys=[configuration_id])

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
