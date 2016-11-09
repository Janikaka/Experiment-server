""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from sqlalchemy import and_
from sqlalchemy.orm import relationship
from .meta import Base
from .users_experimentgroups import users_experimentgroups


class User(Base):
    """ This is definition of class User. """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, index=True)
    dataitems = relationship("DataItem", backref="user", cascade="delete")
    experimentgroups = relationship(
        "ExperimentGroup",
        secondary=users_experimentgroups,
        back_populates="users"
    )

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_total_dataitems_in_experiment(self, exp_id):
        """ 
        Get total count of DataItems, which are sent to the service during Experiment's,
        and in which user has participated to.
        'running' state.
        Params: exp_id: Experiment id in which User belongs to
        Return: total count of DataItems in Experiment sent by User
        """
        from .experiments import Experiment
        from .dataitems import DataItem

        experiment = Experiment.get(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        count = DataItem.query().filter(
            and_(DataItem.user_id == self.id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= end_datetime)).count()
        return count
