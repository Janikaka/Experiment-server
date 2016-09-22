""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)

from .meta import Base


class RangeConstraint(Base):
    """ This is definition of a RangeConstraints class """
    __tablename__ = 'rangeconstraints'
    id = Column(Integer, primary_key=True)
    configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    operator_id = Column(Integer, ForeignKey('operators.id'))
    value = Column(Integer)
