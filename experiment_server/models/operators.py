""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    Text
)

from sqlalchemy.orm import relationship
from .meta import Base


class Operator(Base):
    """
    This is definition of operator class.
    Operators-table contains all possible Operators. Operators are used by Range- and ExclusionConstraints. Currently
    they are following in experiment_server/scripts/initialize.db:
        op1 = Operator(id=1, math_value='=', human_value='equals')
        op2 = Operator(id=2, math_value='<=', human_value='less or equal than')
        op3 = Operator(id=3, math_value='<', human_value='less than')
        op4 = Operator(id=4, math_value='>=', human_value='greater or equal than')
        op5 = Operator(id=5, math_value='>', human_value='greater than')
        op6 = Operator(id=6, math_value='!=', human_value='not equal')
        op7 = Operator(id=7, math_value='[]', human_value='inclusive')
        op8 = Operator(id=8, math_value='()', human_value='exclusive')
        op9 = Operator(id=9, math_value='def', human_value='must define')
        op10 = Operator(id=10, math_value='ndef', human_value='must not define')
    """
    # TODO: Instead of database-table, hard-code operators. There is no need for a table for operators
    __tablename__ = 'operators'
    id = Column(Integer, primary_key=True)
    math_value = Column(Text)
    human_value = Column(Text)
    rangeconstraints = relationship("RangeConstraint", backref="operator")

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
