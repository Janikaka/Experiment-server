""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint

from .meta import Base


class ConfigurationKey(Base):
    """
    This is definition of ConfigurationKey class.
    ConfigurationKey defines what Configurations ExperimentGroup has. Created Configuration's key must be equal to some
    existing ConfigurationKey's name. Both Configuration and ConfigurationKey must belong to same Application.
    """
    __tablename__ = 'configurationkeys'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    rangeconstraints = relationship("RangeConstraint", backref="configurationkey", cascade="delete")
    exclusionconstraints = relationship("ExclusionConstraint",
                                        primaryjoin="or_(ConfigurationKey.id==ExclusionConstraint.first_configurationkey_id,ConfigurationKey.id==ExclusionConstraint.second_configurationkey_id)",
                                        cascade="delete")
    UniqueConstraint('name', 'application_id')


    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
