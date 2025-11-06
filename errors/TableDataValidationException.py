class TableDataValidationException(Exception):
    """Exception raised for Table Data Validator error scenarios.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)