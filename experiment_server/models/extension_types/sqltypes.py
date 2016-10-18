import json
import sqlalchemy.types

"""
Data-model for arbitary data. Use this instead of PickleType.
"""


class JSONType(sqlalchemy.types.PickleType):
    impl = sqlalchemy.types.UnicodeText

    def __init__(self):
        sqlalchemy.types.PickleType.__init__(self, pickler=json)