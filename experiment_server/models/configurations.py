from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base
from sqlalchemy.orm import relationship

class Configuration(Base):
	__tablename__ = 'configurations'
	id = Column(Integer, primary_key=True)
	experimentgroup_id = Column(Integer, ForeignKey('experimentgroups.id'))
	key = Column(Text)
	value = Column(Integer)

