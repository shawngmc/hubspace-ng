"""Define exceptions."""
class HubspaceError(Exception):
    """Define a base exception."""

class InvalidCredentialsError(HubspaceError):
    """Define an exception related to invalid credentials."""

class AuthenticationError(HubspaceError):
    """Define an exception related to invalid credentials."""

class RequestError(HubspaceError):
    """Define an exception related to bad HTTP requests."""
