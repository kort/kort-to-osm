def Error(error):
    for cls in ErrorType.__subclasses__():
        if cls.handles_error(error):
            return cls()
    raise ValueError


class ErrorType(object):
    pass


class ReligionErrorType(ErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'religion'

    def tag():
        return "religion"
