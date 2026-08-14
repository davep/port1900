"""Response object for port1900."""

##############################################################################
# Python imports.
import mimetypes
from dataclasses import dataclass
from functools import cached_property

##############################################################################
# Local imports.
from .uri import NexURI


##############################################################################
@dataclass(frozen=True)
class Response:
    """Represents a response received from a Nex server."""

    uri: NexURI
    """The requested Nex URI."""
    raw_bytes: bytes
    """Raw bytes received from the server."""
    encoding: str = "utf-8"
    """Encoding used to decode text (default: 'utf-8')."""

    @property
    def content(self) -> bytes:
        """Raw response bytes."""
        return self.raw_bytes

    @cached_property
    def text(self) -> str:
        """Response content decoded as text.

        Performs a decode using `encoding`. If a UnicodeDecodeError is raised,
        falls back to `iso8859-1`, and if that raises an error falls back to
        errors="replace".
        """
        try:
            return self.raw_bytes.decode(self.encoding)
        except UnicodeDecodeError:
            try:
                return self.raw_bytes.decode("iso8859-1")
            except UnicodeDecodeError:
                return self.raw_bytes.decode(self.encoding, errors="replace")

    @cached_property
    def lines(self) -> list[str]:
        """Response text split into lines."""
        return self.text.splitlines()

    @property
    def is_directory(self) -> bool:
        """True if the requested URI represents a directory."""
        return self.uri.is_directory

    @cached_property
    def mime_type(self) -> str:
        """Inferred MIME type based on the requested URI path extension.

        Defaults to 'text/plain' if no MIME type can be inferred or if there is no extension.
        """
        guessed, _ = mimetypes.guess_type(self.uri.path)
        return guessed or "text/plain"

    def __repr__(self) -> str:
        return f"<Response [URI: {self.uri}] {len(self.raw_bytes)} bytes>"


### response.py ends here
