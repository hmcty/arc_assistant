class InternalSQLError(Exception):
    """
    Thrown when there's an internal SQL error.
    """

    def __init__(self, message="Internal SQL error, contact admin!"):
        self.message = message
        super().__init__(self.message)