class BaseDemonoidException(ValueError):

    def __init__(self, message):
        super(BaseDemonoidException, self).__init__(message)


class HeadReachedException(BaseDemonoidException):
    """A Paginated list has reached the first page and can't go further back."""


class InvalidSearchParameterException(BaseDemonoidException):
    """A Search instance has received a search criteria (parameter) that's not supported by
       Demonoid's search form."""
