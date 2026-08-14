"""Async Nex protocol client implementation."""

##############################################################################
# Python imports.
import asyncio
import builtins
import time
from contextlib import suppress
from typing import Final, Self

##############################################################################
# Local imports.
from .exceptions import ConnectionError, TimeoutError, URIError
from .response import Response
from .uri import NexURI

##############################################################################
DEFAULT_TIMEOUT: Final[float] = 30.0
"""Default timeout in seconds for Nex network operations."""


##############################################################################
class Client:
    """An asynchronous client for the Nex protocol."""

    def __init__(
        self,
        *,
        timeout: float | None = DEFAULT_TIMEOUT,
        encoding: str = "utf-8",
    ) -> None:
        """Initialise a Nex client instance.

        Args:
            timeout: Default timeout in seconds for requests, or None for no timeout.
            encoding: Default character encoding for response text.
        """
        self._timeout: float | None = timeout
        """Default timeout in seconds for network operations."""

        self._encoding: str = encoding
        """Default text encoding for decoding responses."""

    @property
    def timeout(self) -> float | None:
        """The default timeout in seconds for requests."""
        return self._timeout

    @property
    def encoding(self) -> str:
        """The default character encoding for decoding responses."""
        return self._encoding

    async def request(
        self,
        target: str | NexURI,
        *,
        timeout: float | None = None,
        encoding: str | None = None,
    ) -> Response:
        """Send a Nex request to a server.

        Args:
            target: Either a Nex target string (e.g. 'nex://example.com/hello.txt') or a NexURI.
            timeout: Optional timeout override in seconds for this request.
            encoding: Optional character encoding override for decoding the response.

        Returns:
            A Response instance containing the server output and URI metadata.

        Raises:
            URIError: If the target string cannot be parsed as a valid Nex URI.
            ConnectionError: If network connection to the server fails.
            TimeoutError: If the request times out.
        """
        if isinstance(target, NexURI):
            nex_uri = target
        elif isinstance(target, str):
            nex_uri = NexURI.from_string(target)
        else:
            raise URIError(f"Expected str or NexURI, got {type(target).__name__}")

        effective_timeout = timeout if timeout is not None else self._timeout
        effective_encoding = encoding if encoding is not None else self._encoding

        host = nex_uri.host
        port = nex_uri.port
        command_bytes = nex_uri.request_bytes

        start_time = time.monotonic()
        try:
            if effective_timeout is not None and effective_timeout > 0:
                async with asyncio.timeout(effective_timeout):
                    raw_bytes = await self._send_and_receive(host, port, command_bytes)
            else:
                raw_bytes = await self._send_and_receive(host, port, command_bytes)
        except (TimeoutError, builtins.TimeoutError) as error:
            elapsed = time.monotonic() - start_time
            raise TimeoutError(
                f"Request to {host}:{port} timed out after {elapsed:.2f}s"
            ) from error
        except ConnectionError:
            raise
        except Exception as error:
            raise ConnectionError(
                f"Failed to connect to {host}:{port}: {error}"
            ) from error

        return Response(uri=nex_uri, raw_bytes=raw_bytes, encoding=effective_encoding)

    async def get(
        self,
        target: str | NexURI,
        *,
        timeout: float | None = None,
        encoding: str | None = None,
    ) -> Response:
        """Alias for `request`."""
        return await self.request(target, timeout=timeout, encoding=encoding)

    async def _send_and_receive(self, host: str, port: int, payload: bytes) -> bytes:
        """Open TCP connection, send payload, and read response to EOF."""
        try:
            reader, writer = await asyncio.open_connection(host, port)
        except Exception as error:
            raise ConnectionError(
                f"Failed to connect to {host}:{port}: {error}"
            ) from error

        try:
            writer.write(payload)
            await writer.drain()

            chunks: list[bytes] = []
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        except Exception as error:
            raise ConnectionError(
                f"Error reading response from {host}:{port}: {error}"
            ) from error
        finally:
            writer.close()
            with suppress(Exception):
                await writer.wait_closed()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None:
        pass


### client.py ends here
