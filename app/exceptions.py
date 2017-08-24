class ProcessingError(Exception):
    """The super class for all custom exceptions."""

class NonexistentDocumentException(ProcessingError):
    """Raise when a document is not found."""

class DuplicateDocumentException(ProcessingError):
    """Raise when an incoming document is a duplicate."""

class InvalidDocumentStructureException(ProcessingError):
    """Raise when incoming document structure validation fails."""

class InvalidDocumentTypeException(ProcessingError):
    """Raise when incoming document type validation fails."""

class BadTokenException(ProcessingError):
    """Raise when a JWT has expired or has invalid syntax."""

class DocumentQuotaExceeded(ProcessingError):
    """Raise when a user has submitted more documents
    than allowed in app.config.server.free_quota."""
