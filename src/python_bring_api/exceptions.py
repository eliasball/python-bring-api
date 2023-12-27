"""Exceptions for OpenData transport API client."""


class BringError(Exception):
    """General BringError exception occurred."""

    pass


class BringAuthError(BringError):
    """When a authentication error is encountered."""

    pass

class BringConnectionError(BringError):
    """When a connection error is encountered."""

    pass
