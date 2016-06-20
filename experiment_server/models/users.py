from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    dataitems = relationship("DataItems")

Index('users_index', Users.username, unique=True, mysql_length=255)
