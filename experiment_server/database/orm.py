from experiment_server.models import DBSession

"""
Used as a base class for every model to ensure ORM-style.
Add new common orm-related functions here.
"""


class ORM:
    @classmethod
    def query(class_):
        return DBSession.query(class_)

    @classmethod
    def get(class_, id):
        return DBSession.query(class_).get(id)

    @classmethod
    def get_all(class_):
        return DBSession.query(class_).all()
