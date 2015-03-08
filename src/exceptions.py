class HeadReachedException(ValueError):

    def __init__(self):
        message = 'Reached head of Paginated List. Can\'t go to previous!'
        super(HeadReachedException, self).__init__(message)
