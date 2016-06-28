from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base

from sqlalchemy.orm import relationship

class Configurations(Base):
	__tablename__ = 'configurations'
	id = Column(Integer, primary_key=True)
	key = Column(Text)
	value = Column(Integer)
	experimentgroup_id = Column(Integer, ForeignKey('experimentgroups.id'))
	#experimentgroup = relationship("Experimentgroups", backref="experimentgroup", cascade="delete")
