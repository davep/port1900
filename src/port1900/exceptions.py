"""Exception hierarchy for the port1900 Nex client library."""


##############################################################################
class Port1900Error(Exception):
    """Base exception class for all port1900 errors."""


##############################################################################
class URIError(Port1900Error):
    """Exception raised when a Nex URI is invalid or parsing fails."""


##############################################################################
class ConnectionError(Port1900Error):
    """Exception raised when a network connection to a Nex server fails."""


##############################################################################
class TimeoutError(Port1900Error):
    """Exception raised when a network operation times out."""


### exceptions.py ends here
