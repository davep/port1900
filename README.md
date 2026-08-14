# Port1900: Async Nex Protocol Client Library

Port1900 is an async-first, fully type-hinted Python client library for the Nex protocol.

## Features

- **Async First**: Built on top of Python's standard `asyncio` networking loop.
- **Nex Protocol Support**: Connection management, path transmission, stateless retrieval, and directory detection.
- **Type Safe**: Fully typed API passing strict static type checking (`mypy --strict`).
- **NexURI Representation**: Rich URI class to parse, inspect, validate, manipulate, and resolve Nex URIs.
- **Zero Dependencies**: Built entirely on Python's standard library.
- **CLI Utility**: Includes a `port1900` command-line interface out of the box.

---

## Installation

`port1900` requires Python 3.12 or later and can be installed with your package manager of choice.

With `pip`:

```shell
pip install port1900
```

With `uv`:

```shell
uv add port1900
```

---

## Quick Start

### 1. Make a Simple Request

Use `Client` with standard async context managers to query a Nex server:

```python
import asyncio
from port1900 import Client, Port1900Error

async def main():
    async with Client() as client:
        try:
            # Query a Nex document or directory
            response = await client.request("nex://nex.nightfall.city/")

            print(f"Target host: {response.uri.host}")
            print(f"Is directory: {response.is_directory}")
            print(f"Content length: {len(response.content)} bytes")
            print("--- Response Text ---")
            print(response.text)
        except Port1900Error as error:
            print(f"Request failed: {error}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Working with `NexURI`

The `NexURI` class parses full URI strings (`nex://host/path`) or path targets:

```python
from port1900 import NexURI

# Parse from Nex URI string
uri = NexURI.from_string("nex://nex.nightfall.city/hello-world.txt")

print(uri.host)          # 'nex.nightfall.city'
print(uri.port)          # 1900
print(uri.path)          # '/hello-world.txt'
print(uri.request_path)  # 'hello-world.txt'
print(uri.is_directory)  # False

# Create modified copies
custom_port_uri = uri.with_port(1905)
parent_uri = uri.parent
root_uri = uri.root
```

---

## Command Line Interface (CLI)

`port1900` includes a command-line client:

```bash
# Query a Nex target (defaults to nex://nex.nightfall.city/)
uv run port1900 nex://nex.nightfall.city/

# Query on a custom port
uv run port1900 -p 1905 nex://example.com/hello-world.txt

# Output raw binary content to stdout
uv run port1900 -r nex://nex.nightfall.city/image.png

# Display CLI help
uv run port1900 --help
```

---

## Licence

MIT

[//]: # (README.md ends here)
