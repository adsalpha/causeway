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
