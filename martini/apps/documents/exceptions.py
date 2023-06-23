class UnprocessableDocumentError(Exception):
    '''A custom exception raised when a document cannot be processed.'''

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
