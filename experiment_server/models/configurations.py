from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    PickleType
)

from .meta import Base
from sqlalchemy.orm import relationship

class Configuration(Base):
	__tablename__ = 'configurations'
	id = Column(Integer, primary_key=True)
	experimentgroup_id = Column(Integer, ForeignKey('experimentgroups.id'))
	key = Column(Text)
	value = Column(PickleType)

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}
