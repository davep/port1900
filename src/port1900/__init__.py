"""An async-first, fully-typed client library for the Nex protocol."""

##############################################################################
# Python imports.
from importlib.metadata import version

##############################################################################
# Main library information.
__author__ = "Dave Pearson"
__copyright__ = "Copyright 2026, Dave Pearson"
__credits__ = ["Dave Pearson"]
__maintainer__ = "Dave Pearson"
__email__ = "davep@davep.org"
__version__: str = version("port1900")
__licence__ = "MIT"

##############################################################################
# Local imports.
from .client import DEFAULT_TIMEOUT, Client
from .exceptions import (
    ConnectionError,
    Port1900Error,
    TimeoutError,
    URIError,
)
from .response import Response
from .uri import (
    NEX_DEFAULT_PORT,
    NEX_PREFIX,
    NEX_SCHEME,
    NexURI,
)

##############################################################################
# Public API.
__all__ = [
    "DEFAULT_TIMEOUT",
    "NEX_DEFAULT_PORT",
    "NEX_PREFIX",
    "NEX_SCHEME",
    "Client",
    "ConnectionError",
    "NexURI",
    "Port1900Error",
    "Response",
    "TimeoutError",
    "URIError",
]

### __init__.py ends here
