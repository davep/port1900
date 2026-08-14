# Getting Started

This guide introduces the primary components of Port1900 and demonstrates how to execute Nex requests, parse URIs, and handle errors.

All of the public classes, constants, and exceptions are exposed at the top level of the package. You can import them directly from `port1900`.

## Core Components

The following classes form the core interface of the library:

- **[Client][port1900.client.Client]**: The asynchronous client used to configure and dispatch requests over TCP port 1900.
- **[Response][port1900.response.Response]**: Represents the server's response, exposing the target URI (`uri`), decoded response text (`text`), response lines (`lines`), raw bytes (`raw_bytes`), directory indicator (`is_directory`), and MIME type inference (`mime_type`).
- **[NexURI][port1900.uri.NexURI]**: A utility class to parse, validate, and manipulate Nex URIs and target strings safely.
- **[Port1900Error][port1900.exceptions.Port1900Error]**: The base exception class for all errors raised by the library.

---

## Basic Request

To execute a request, initialise a [Client][port1900.client.Client] and call its [request][port1900.client.Client.request] method. The client automatically resolves target host details and executes the network connection:

```python
import asyncio
from port1900 import Client, Port1900Error

async def main():
    async with Client() as client:
        try:
            # Execute the request (accepts a URI string or a NexURI)
            response = await client.request("nex://nex.nightfall.city/")

            print(f"Target Host: {response.uri.host}")
            print(f"Is Directory: {response.is_directory}")
            print(f"MIME Type:   {response.mime_type}")
            print(f"Content Length: {len(response.content)} bytes")
            print("--- Response Body ---")
            print(response.text)

        except Port1900Error as error:
            print(f"Request failed: {error}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Working with `NexURI`

The [NexURI][port1900.uri.NexURI] class allows you to parse both full URI strings (`nex://nex.nightfall.city/hello-world.txt`) and target format strings (`nex.nightfall.city/hello-world.txt`):

```python
from port1900 import NexURI

# Parse from a Nex URI string
uri = NexURI.from_string("nex://nex.nightfall.city/hello-world.txt")

print(uri.host)          # 'nex.nightfall.city'
print(uri.port)          # 1900
print(uri.path)          # '/hello-world.txt'
print(uri.request_path)  # 'hello-world.txt'
print(uri.is_directory)  # False

# NexURI objects are immutable; construct new instances with updated parts
custom_port_uri = uri.with_port(1905)
parent_uri = uri.parent
root_uri = uri.root
```

---

## Exception Hierarchy

All exceptions raised by the library inherit from the base class [Port1900Error][port1900.exceptions.Port1900Error]. When managing errors, you can catch specific subclasses for finer control:

- **[URIError][port1900.exceptions.URIError]**: Raised when a given URI or target string cannot be parsed or validated.
- **[ConnectionError][port1900.exceptions.ConnectionError]**: Raised when network connections to the Nex server fail or are refused.
- **[TimeoutError][port1900.exceptions.TimeoutError]**: Raised when a Nex query operation times out.


---

[//]: # (getting_started.md ends here)
