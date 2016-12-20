""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from .meta import Base

from .extension_types.sqltypes import JSONType


class ExclusionConstraint(Base):
    """
    This is definition of exclusion constraints class.
    ExclusionConstraint defines what kind of Configurations can be set on ExperimentGroup. If either argument, first or
    second is true, then the other must be true. When creating Configuration which tries to violate an
    ExclusionConstraint, creating it will be prevented.
    First and second value both have a- and b-values. They are required for Operators 'inclusive' and 'exclusive'. In
    all other cases b-values can be disregarded.
    """
    __tablename__ = 'exclusionconstraints'
    id = Column(Integer, primary_key=True)
    first_configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    first_operator_id = Column(Integer, ForeignKey('operators.id'))
    first_value_a = Column(Text)
    first_value_b = Column(Text)

    second_configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    second_operator_id = Column(Integer, ForeignKey('operators.id'))
    second_value_a = Column(Text)
    second_value_b = Column(Text)

    first_configurationkey = relationship("ConfigurationKey", foreign_keys=[first_configurationkey_id])
    first_operator = relationship("Operator", foreign_keys=[first_operator_id])
    second_configurationkey = relationship("ConfigurationKey", foreign_keys=[second_configurationkey_id])
    second_operator = relationship("Operator", foreign_keys=[second_operator_id])

    def as_dict(self):
        """ transfer data to dictionary """
        new_dict = {'id': getattr(self, 'id'),
                    'first_configurationkey_id': getattr(self, 'first_configurationkey_id'),
                    'first_operator_id': getattr(self, 'first_operator_id'),
                    'first_value': [getattr(self, 'first_value_a'), getattr(self, 'first_value_b')],
                    'second_configurationkey_id': getattr(self, 'second_configurationkey_id'),
                    'second_operator_id': getattr(self, 'second_operator_id'),
                    'second_value': [getattr(self, 'second_value_a'), getattr(self, 'second_value_b')]}
        #return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
        return new_dict
