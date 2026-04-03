class ApiError(Exception):
    """Application error with an HTTP-friendly status code and machine code."""

    def __init__(self, message: str, code: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
