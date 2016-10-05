"""
Used as a base class for every model to ensure ORM-style.
Add new common orm-related functions here.
"""

DBSession = None

class ORM:
    @classmethod
    def query(class_):
        return DBSession.query(class_)

    @classmethod
    def get(class_, id):
        return DBSession.query(class_).get(id)

    """
        Get by wanted field: value
    """
    @classmethod
    def get_by(cls, field, value):
        return DBSession.query(cls).filter(getattr(cls, field) == value).first()

    @classmethod
    def all(class_):
        return DBSession.query(class_).all()

    @classmethod
    def save(cls, data):
        DBSession.add(data)
        DBSession.flush()

    @classmethod
    def destroy(cls, data):
        return DBSession.delete(data)

    """
        Update via primary id
    """
    @classmethod
    def update(cls, primary_id, key, new_value):
        return DBSession.query(cls).filter(getattr(cls, id) == primary_id)\
                                   .update({key: new_value})
