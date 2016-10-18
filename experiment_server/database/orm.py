"""
Used as a base class for every model to ensure ORM-style.
Add new common orm-related functions here.
Usage. <className>.<function>
"""

DBSession = None


class ORM:
    @classmethod
    def query(cls):
        """
        Builder for custom queries
        """
        return DBSession.query(cls)

    @classmethod
    def get(cls, id):
        """
        Get's object by its ID
        :param id: id of the class
        """
        return DBSession.query(cls).get(id)

    @classmethod
    def get_by(cls, field, value):
        """
        Get object by its field.
        :param field: field to run query on
        :param value: value that the field must match
        """
        return DBSession.query(cls).filter(getattr(cls, field) == value).first()

    @classmethod
    def all(cls):
        """
        Get all results that have the type <class>
        """
        return DBSession.query(cls).all()

    @classmethod
    def save(cls, data):
        """
        Save a model to the database.

        Example:
            <modelT>.save(<modelT>)

        :param data: Model to be saved
        """
        DBSession.add(data)
        DBSession.flush()

    @classmethod
    def destroy(cls, data):
        """
        Delete model from the database

        Example:
            <modelT>.destroy(<modelT>)

        :param data: model to be deleted
        """
        return DBSession.delete(data)

    @classmethod
    def update(cls, primary_id, key, new_value):
        """
        Update model key
        :param primary_id: id of the model
        :param key: field to be updated
        :param new_value: new value for the field
        """
        DBSession.query(cls).filter(getattr(cls, 'id') == primary_id)\
                                   .update({key: new_value})
        DBSession.flush()