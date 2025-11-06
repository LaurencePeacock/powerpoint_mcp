class ChartDataConverterException(Exception):
    """Exception raised for Chart Data Converter error scenarios.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)