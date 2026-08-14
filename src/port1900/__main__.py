"""Command-line interface entry point for the port1900 Nex client."""

##############################################################################
# Python imports.
import argparse
import asyncio
import sys

##############################################################################
# Local imports.
from .client import DEFAULT_TIMEOUT, Client
from .exceptions import ConnectionError, Port1900Error, TimeoutError, URIError
from .uri import NexURI


##############################################################################
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        The parsed Namespace object.
    """
    parser = argparse.ArgumentParser(
        prog="port1900",
        description="Async Nex protocol client library.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="nex://nex.nightfall.city/",
        help="Target Nex URI string (default: nex://nex.nightfall.city/).",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=None,
        help="Override TCP port number.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Network timeout in seconds (default: 30.0).",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="Text encoding for response (default: utf-8).",
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Output raw binary response content to stdout.",
    )
    return parser.parse_args()


##############################################################################
async def run_cli(
    target: str,
    port: int | None,
    timeout: float,
    encoding: str,
    raw: bool,
) -> int:
    """Execute the Nex CLI request asynchronously.

    Args:
        target: Target Nex URI string.
        port: Optional TCP port override.
        timeout: Network timeout in seconds.
        encoding: Response text encoding.
        raw: True to output raw binary response.

    Returns:
        Exit code integer (0 for success, 1 for error).
    """
    try:
        uri = NexURI.from_string(target)
        if port is not None:
            uri = uri.with_port(port)

        async with Client(timeout=timeout, encoding=encoding) as client:
            response = await client.request(uri)
            if raw:
                sys.stdout.buffer.write(response.content)
            else:
                sys.stdout.write(response.text)
                if response.text and not response.text.endswith("\n"):
                    sys.stdout.write("\n")
            sys.stdout.flush()
            return 0
    except (URIError, ConnectionError, TimeoutError, Port1900Error) as error:
        sys.stderr.write(f"port1900: error: {error}\n")
        return 1
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"port1900: unexpected error: {error}\n")
        return 1


##############################################################################
def main() -> None:
    """Main entry point for the port1900 command-line client."""
    parsed = parse_args()
    try:
        exit_code = asyncio.run(
            run_cli(
                target=parsed.target,
                port=parsed.port,
                timeout=parsed.timeout,
                encoding=parsed.encoding,
                raw=parsed.raw,
            )
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.stderr.write("\nport1900: interrupted\n")
        sys.exit(130)


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
