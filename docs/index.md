# Port1900: Async Nex Protocol Client Library

Port1900 is an asynchronous, object-oriented, fully type-hinted client library for the Nex protocol. It is designed to target Python 3.12 and later, relying entirely on the Python standard library.

Features of the library:

- **Asynchronous throughout**: Built on top of standard `asyncio` for non-blocking I/O.
- **Strictly typed**: Complete type safety utilising modern Python standards, strictly avoiding `Any`.
- **Nex Protocol Support**: Full support for Nex network connection, path transmission, stateless retrieval, directory detection, and MIME type inference.
- **NexURI representation**: Powerful object-oriented representation to parse, validate, and manipulate Nex URIs and target strings.
- **Zero dependencies**: Relies only on Python's standard library.
- **CLI utility**: Includes a command-line interface out of the box.

## Installation

You can install Port1900 in your environment. The recommended tool for modern Python projects is `uv`, but standard `pip` is also fully supported.

### Using uv

To add Port1900 to your project as a dependency:

```bash
uv add port1900
```

To install Port1900 directly into your active virtual environment:

```bash
uv pip install port1900
```

To run the Port1900 command-line interface without installing it globally:

```bash
uvx port1900 nex://nex.nightfall.city/
```

### Using pip

To install Port1900 from PyPI using standard packaging tools:

```bash
pip install port1900
```

[//]: # (index.md ends here)
