class ServiceError(Exception):
    def __init__(self, code="SERVICE_ERROR", message="Service error", details=None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
