from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from sqlalchemy.orm import relationship
from .meta import Base
from .users_experimentgroups import Users_Experimentgroups


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    dataitems = relationship("DataItems", backref="user", cascade="delete")
    experimentgroups = relationship(
    	"ExperimentGroups",
    	secondary=Users_Experimentgroups,
    	back_populates="users"
    )

Index('users_index', Users.username, unique=True, mysql_length=255)
