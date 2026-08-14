"""Tests for command-line interface entry point."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import suppress

import pytest

from port1900.__main__ import main, parse_args, run_cli


@pytest.fixture
async def mock_cli_server() -> AsyncGenerator[int, None]:
    """Start mock server for CLI test."""

    async def handle_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        await reader.readline()
        writer.write(b"CLI Test Content\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    server_task = asyncio.create_task(server.serve_forever())

    yield port

    server.close()
    await server.wait_closed()
    server_task.cancel()
    with suppress(asyncio.CancelledError):
        await server_task


def test_parse_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv", ["port1900", "nex://example.com/test", "-p", "1901"]
    )
    args = parse_args()
    assert args.target == "nex://example.com/test"
    assert args.port == 1901
    assert not args.raw


@pytest.mark.asyncio
async def test_run_cli_success(
    mock_cli_server: int, capsys: pytest.CaptureFixture[str]
) -> None:
    port = mock_cli_server
    target = f"nex://127.0.0.1:{port}/"

    exit_code = await run_cli(
        target=target,
        port=None,
        timeout=5.0,
        encoding="utf-8",
        raw=False,
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "CLI Test Content" in captured.out


@pytest.mark.asyncio
async def test_run_cli_raw(
    mock_cli_server: int, caplog: pytest.LogCaptureFixture
) -> None:
    port = mock_cli_server
    target = f"nex://127.0.0.1:{port}/"

    exit_code = await run_cli(
        target=target,
        port=None,
        timeout=5.0,
        encoding="utf-8",
        raw=True,
    )
    assert exit_code == 0


@pytest.mark.asyncio
async def test_run_cli_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = await run_cli(
        target="invalid_uri://bad",
        port=None,
        timeout=1.0,
        encoding="utf-8",
        raw=False,
    )
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "port1900: error:" in captured.err


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["port1900", "nex://example.com/"])

    async def mock_run_cli(*args: object, **kwargs: object) -> int:
        return 0

    monkeypatch.setattr("port1900.__main__.run_cli", mock_run_cli)
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["port1900", "nex://example.com/"])

    async def mock_run_cli(*args: object, **kwargs: object) -> int:
        raise KeyboardInterrupt()

    monkeypatch.setattr("port1900.__main__.run_cli", mock_run_cli)
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 130
