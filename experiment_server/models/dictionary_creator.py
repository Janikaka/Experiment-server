class DictionaryCreator:
    def as_dict(self):
        """ transfer data to dictionary """
        result = {}
        for col in self.__table__.columns:
            if col.name == 'startDatetime' or col.name == 'endDatetime':
                # col.name means data from column
                result[col.name] = str(getattr(self, col.name))
            else:
                result[col.name] = getattr(self, col.name)
        return result
