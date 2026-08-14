"""Nex URI representation and parsing."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
from pathlib import Path
from typing import Final, Self
from urllib.parse import (
    quote,
    unquote,
    urljoin,
    urlparse,
    uses_fragment,
    uses_netloc,
    uses_params,
    uses_query,
    uses_relative,
)

##############################################################################
# Local imports.
from .exceptions import URIError

##############################################################################
NEX_SCHEME: Final[str] = "nex"
"""The default URL scheme for the Nex protocol."""
NEX_PREFIX: Final[str] = f"{NEX_SCHEME}://"
"""The standard prefix for Nex URIs."""
NEX_DEFAULT_PORT: Final[int] = 1900
"""The default TCP network port for the Nex protocol."""


##############################################################################
def _normalise_scheme(uri: str) -> str:
    """Normalise the scheme portion of a URI to lowercase."""
    scheme, separator, rest = uri.partition("://")
    return f"{scheme.lower()}{separator}{rest}" if separator else uri


##############################################################################
class _UnsetType:
    """Sentinel class to distinguish between omitted arguments and None."""


_UNSET: Final[_UnsetType] = _UnsetType()
"""Sentinel value to indicate that an argument has not been provided."""


##############################################################################
class NexURI:
    """Represents a validated Nex protocol URI."""

    def __init__(self, uri: str | NexURI) -> None:
        """Initialise and validate a Nex URI.

        Args:
            uri: The raw URI string or an existing NexURI to clone.

        Raises:
            URIError: If the URI is empty, the scheme is missing or not 'nex',
                the host is missing or invalid, or if parsing of the URI fails.
        """
        self._scheme: str
        self._host: str
        self._port: int
        self._path: str

        if isinstance(uri, NexURI):
            self._scheme = uri.scheme
            self._host = uri.host
            self._port = uri.port
            self._path = uri.path
            return

        if not uri or not uri.strip():
            raise URIError("URI cannot be empty")

        cleaned = _normalise_scheme(uri.strip())
        to_parse = (
            "https://" + cleaned.removeprefix(NEX_PREFIX)
            if cleaned.startswith(NEX_PREFIX)
            else cleaned
        )

        try:
            parsed = urlparse(to_parse)
            scheme = parsed.scheme.lower()
            if scheme == "https" and cleaned.startswith(NEX_PREFIX):
                scheme = NEX_SCHEME

            if not scheme:
                raise URIError("URI scheme is missing")
            if scheme != NEX_SCHEME:
                raise URIError(
                    f"Invalid URI scheme: '{scheme}'. Expected '{NEX_SCHEME}'"
                )

            if not parsed.hostname:
                raise URIError("URI host is missing or invalid")

            self._scheme = scheme
            self._host = parsed.hostname
            self._port = parsed.port if parsed.port is not None else NEX_DEFAULT_PORT

            raw_path = unquote(parsed.path)
            if not raw_path:
                self._path = "/"
            else:
                self._path = raw_path if raw_path.startswith("/") else f"/{raw_path}"

        except URIError:
            raise
        except Exception as error:
            raise URIError(f"Failed to parse URI: {error}") from error

    _KNOWN_SCHEMES: Final[set[str]] = {
        scheme
        for scheme in (
            NEX_SCHEME,
            *uses_netloc,
            *uses_params,
            *uses_relative,
            *uses_query,
            *uses_fragment,
        )
        if scheme
    }
    """Set of known URI schemes for validation."""

    @classmethod
    def with_default_scheme(cls, uri: str) -> Self:
        """Add the Nex scheme to a URI if it is missing.

        Args:
            uri: The URI string to check and potentially modify.

        Returns:
            A new NexURI instance with the scheme added if it was missing.

        Raises:
            URIError: If the URI is invalid or missing required components.
        """
        cleaned = uri.strip()
        if cleaned and not cleaned.startswith(NEX_PREFIX) and "://" not in cleaned:
            cleaned = f"{NEX_PREFIX}{cleaned}"
        return cls(cleaned)

    @classmethod
    def from_string(cls, target: str) -> Self:
        """Create a NexURI from a target string or URI.

        Args:
            target: The target string or Nex URI.

        Returns:
            A new NexURI instance.

        Raises:
            URIError: If parsing fails or required host is missing.
        """
        if not target or not target.strip():
            raise URIError("URI cannot be empty")
        return cls.with_default_scheme(target)

    @property
    def scheme(self) -> str:
        """The URI scheme (always 'nex')."""
        return self._scheme

    @property
    def host(self) -> str:
        """The target hostname or IP address."""
        return self._host

    @property
    def port(self) -> int:
        """The target port (defaults to `NEX_DEFAULT_PORT`)."""
        return self._port

    @property
    def path(self) -> str:
        """The resource path portion of the URI (e.g. '/' or '/hello-world.txt')."""
        return self._path

    @property
    def request_path(self) -> str:
        """The resource path sent to the server (without leading slash)."""
        if self._path == "/":
            return ""
        return self._path.removeprefix("/")

    @property
    def request_string(self) -> str:
        """Return the path payload string sent over TCP to the Nex server."""
        return f"{self.request_path}\r\n"

    @property
    def request_bytes(self) -> bytes:
        """Return the path payload bytes sent over TCP to the Nex server."""
        return self.request_string.encode("utf-8")

    @property
    def is_directory(self) -> bool:
        """True if an empty path or a path finishing with '/'."""
        return self.request_path == "" or self.request_path.endswith("/")

    def replace(
        self,
        *,
        host: str | _UnsetType = _UNSET,
        port: int | _UnsetType = _UNSET,
        path: str | _UnsetType = _UNSET,
    ) -> Self:
        """Create a new NexURI by replacing specific parts of this URI."""
        new_host = self._host if isinstance(host, _UnsetType) else host
        new_port = self._port if isinstance(port, _UnsetType) else port
        new_path = self._path if isinstance(path, _UnsetType) else path

        if not new_path.startswith("/"):
            new_path = f"/{new_path}"

        port_str = f":{new_port}" if new_port != NEX_DEFAULT_PORT else ""
        path_quoted = quote(new_path)
        new_uri_str = f"{NEX_PREFIX}{new_host}{port_str}{path_quoted}"
        return self.__class__(new_uri_str)

    def with_host(self, host: str) -> Self:
        """Return a new NexURI with the host replaced."""
        return self.replace(host=host)

    def with_port(self, port: int) -> Self:
        """Return a new NexURI with the port replaced."""
        return self.replace(port=port)

    def with_path(self, path: str) -> Self:
        """Return a new NexURI with the path replaced."""
        return self.replace(path=path)

    @property
    def parent(self) -> Self:
        """Return a NexURI representing the parent directory of this URI's path."""
        req_path = self.request_path
        if not req_path:
            return self
        parent_path = str(Path(req_path).parent)
        new_path = "/" if parent_path in (".", "/") else f"/{parent_path}/"
        return self.with_path(new_path)

    @property
    def root(self) -> Self:
        """Return a NexURI representing the root directory of this URI's host."""
        return self.with_path("/")

    def resolve(self, relative_uri: str) -> Self:
        """Resolve a relative URI string against this URI as a base.

        Args:
            relative_uri: The relative or absolute target URI string.

        Returns:
            A new NexURI representing the resolved target.

        Raises:
            URIError: If resolution fails or target is invalid.
        """
        base_str = str(self)
        base_http = base_str.replace(NEX_PREFIX, "https://", 1)

        relative_cleaned = _normalise_scheme(relative_uri.strip())
        relative_http = relative_cleaned
        if relative_cleaned.startswith(NEX_PREFIX):
            relative_http = "https://" + relative_cleaned.removeprefix(NEX_PREFIX)

        try:
            resolved_http = urljoin(base_http, relative_http)
            resolved_nex = resolved_http.replace("https://", NEX_PREFIX, 1)
            return self.__class__(resolved_nex)
        except Exception as error:
            raise URIError(
                f"Failed to resolve relative URI '{relative_uri}' against base '{base_str}': {error}"
            ) from error

    def __str__(self) -> str:
        port_str = f":{self._port}" if self._port != NEX_DEFAULT_PORT else ""
        path_quoted = quote(self._path)
        return f"{NEX_PREFIX}{self._host}{port_str}{path_quoted}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = NexURI(other)
            except URIError:
                return False
        if not isinstance(other, NexURI):
            return NotImplemented
        return (
            self.scheme == other.scheme
            and self.host == other.host
            and self.port == other.port
            and self.path == other.path
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._scheme,
                self._host,
                self._port,
                self._path,
            )
        )

    def __len__(self) -> int:
        return len(str(self))


### uri.py ends here
