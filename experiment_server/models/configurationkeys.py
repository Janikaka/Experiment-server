""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)


from .meta import Base


class ConfigurationKey(Base):
    """ This is definition of Configurationkey class """
    __tablename__ = 'configurationkeys'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(Text)
    type = Column(Text)