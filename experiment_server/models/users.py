from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from sqlalchemy.orm import relationship
from .meta import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    dataitems = relationship("DataItems", back_populates="user")

Index('users_index', Users.username, unique=True, mysql_length=255)
