"""Integration and unit tests for Nex Client."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import suppress

import pytest

from port1900.client import DEFAULT_TIMEOUT, Client
from port1900.exceptions import ConnectionError, TimeoutError, URIError
from port1900.uri import NexURI


@pytest.fixture
async def mock_nex_server() -> AsyncGenerator[tuple[int, list[bytes]], None]:
    """Start an async mock Nex server for testing."""
    received_requests: list[bytes] = []

    async def handle_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        data = await reader.readline()
        received_requests.append(data)

        path = data.decode("utf-8").strip()
        if path == "slow":
            await asyncio.sleep(0.5)
            writer.write(b"slow response")
        elif path == "hello.txt":
            writer.write(b"Hello World from Nex!")
        elif path == "dir/":
            writer.write(b"=> nex://my-site.net\n=> about.txt\n")
        elif path == "":
            writer.write(b"Root index content")
        else:
            writer.write(f"Content for {path}".encode())

        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    server_task = asyncio.create_task(server.serve_forever())

    yield port, received_requests

    server.close()
    await server.wait_closed()
    server_task.cancel()
    with suppress(asyncio.CancelledError):
        await server_task


@pytest.mark.asyncio
async def test_client_request(mock_nex_server: tuple[int, list[bytes]]) -> None:
    port, received = mock_nex_server
    uri_str = f"nex://127.0.0.1:{port}/hello.txt"

    async with Client() as client:
        assert client.timeout == DEFAULT_TIMEOUT
        assert client.encoding == "utf-8"

        response = await client.request(uri_str)
        assert response.text == "Hello World from Nex!"
        assert response.raw_bytes == b"Hello World from Nex!"
        assert received[-1] == b"hello.txt\r\n"


@pytest.mark.asyncio
async def test_client_get_alias(mock_nex_server: tuple[int, list[bytes]]) -> None:
    port, received = mock_nex_server
    uri = NexURI(f"nex://127.0.0.1:{port}/dir/")

    async with Client() as client:
        response = await client.get(uri)
        assert "=> about.txt" in response.text
        assert response.is_directory
        assert received[-1] == b"dir/\r\n"


@pytest.mark.asyncio
async def test_client_empty_path(mock_nex_server: tuple[int, list[bytes]]) -> None:
    port, received = mock_nex_server
    uri = NexURI(f"nex://127.0.0.1:{port}")

    async with Client() as client:
        response = await client.request(uri)
        assert response.text == "Root index content"
        assert received[-1] == b"\r\n"


@pytest.mark.asyncio
async def test_client_timeout(mock_nex_server: tuple[int, list[bytes]]) -> None:
    port, _ = mock_nex_server
    uri_str = f"nex://127.0.0.1:{port}/slow"

    client = Client(timeout=0.05)
    with pytest.raises(TimeoutError, match="timed out"):
        await client.request(uri_str)


@pytest.mark.asyncio
async def test_connection_error() -> None:
    # Port 1 is reserved / unusable locally
    client = Client(timeout=1.0)
    with pytest.raises(ConnectionError, match="Failed to connect"):
        await client.request("nex://127.0.0.1:1/file")


@pytest.mark.asyncio
async def test_invalid_target_type() -> None:
    client = Client()
    with pytest.raises(URIError, match="Expected str or NexURI"):
        await client.request(12345)  # type: ignore[arg-type]
