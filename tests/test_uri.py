"""Unit tests for NexURI parsing and manipulation."""

import pytest

from port1900.exceptions import URIError
from port1900.uri import (
    NEX_DEFAULT_PORT,
    NEX_PREFIX,
    NEX_SCHEME,
    NexURI,
)


def test_constants() -> None:
    assert NEX_SCHEME == "nex"
    assert NEX_PREFIX == "nex://"
    assert NEX_DEFAULT_PORT == 1900


def test_basic_uri_parsing() -> None:
    uri = NexURI("nex://nex.nightfall.city/hello-world.txt")
    assert uri.scheme == "nex"
    assert uri.host == "nex.nightfall.city"
    assert uri.port == 1900
    assert uri.path == "/hello-world.txt"
    assert uri.request_path == "hello-world.txt"
    assert uri.request_string == "hello-world.txt\r\n"
    assert uri.request_bytes == b"hello-world.txt\r\n"
    assert not uri.is_directory


def test_empty_path_directory() -> None:
    uri = NexURI("nex://nex.nightfall.city")
    assert uri.path == "/"
    assert uri.request_path == ""
    assert uri.request_string == "\r\n"
    assert uri.request_bytes == b"\r\n"
    assert uri.is_directory

    uri_slash = NexURI("nex://nex.nightfall.city/")
    assert uri_slash.path == "/"
    assert uri_slash.request_path == ""
    assert uri_slash.is_directory


def test_directory_path_ending_in_slash() -> None:
    uri = NexURI("nex://nex.nightfall.city/docs/")
    assert uri.path == "/docs/"
    assert uri.request_path == "docs/"
    assert uri.request_string == "docs/\r\n"
    assert uri.is_directory


def test_custom_port() -> None:
    uri = NexURI("nex://example.org:9999/path")
    assert uri.port == 9999
    assert str(uri) == "nex://example.org:9999/path"


def test_from_string_and_default_scheme() -> None:
    uri1 = NexURI.from_string("nex.nightfall.city/hello.txt")
    assert uri1.scheme == "nex"
    assert uri1.host == "nex.nightfall.city"
    assert uri1.request_path == "hello.txt"

    uri2 = NexURI.with_default_scheme("example.com:1900/dir/")
    assert uri2.host == "example.com"
    assert uri2.is_directory


def test_invalid_uris() -> None:
    with pytest.raises(URIError, match="empty"):
        NexURI("")

    with pytest.raises(URIError, match="empty"):
        NexURI.from_string("   ")

    with pytest.raises(URIError, match="Invalid URI scheme"):
        NexURI("gopher://example.com/")

    with pytest.raises(URIError, match="host is missing"):
        NexURI("nex:///")


def test_clone_and_equality() -> None:
    uri1 = NexURI("nex://example.com/test")
    uri2 = NexURI(uri1)
    assert uri1 == uri2
    assert uri1 == "nex://example.com/test"
    assert uri1 != "invalid-uri"
    assert uri1 != "nex://example.com/other"
    assert hash(uri1) == hash(uri2)
    assert repr(uri1) == "NexURI('nex://example.com/test')"
    assert len(uri1) == len("nex://example.com/test")


def test_with_helpers() -> None:
    uri = NexURI("nex://example.com/original")
    u_host = uri.with_host("other.com")
    assert u_host.host == "other.com"
    assert u_host.path == "/original"

    u_port = uri.with_port(2000)
    assert u_port.port == 2000

    u_path = uri.with_path("/new/path")
    assert u_path.path == "/new/path"


def test_parent_and_root() -> None:
    uri = NexURI("nex://example.com/a/b/c.txt")
    assert uri.parent == "nex://example.com/a/b/"
    assert uri.parent.parent == "nex://example.com/a/"
    assert uri.root == "nex://example.com/"

    root_uri = NexURI("nex://example.com/")
    assert root_uri.parent == "nex://example.com/"


def test_resolve_relative_uris() -> None:
    base = NexURI("nex://my-site.net/dir/page.txt")

    res_absolute = base.resolve("nex://other-site.net/file")
    assert res_absolute == "nex://other-site.net/file"

    res_relative_file = base.resolve("about.txt")
    assert res_relative_file == "nex://my-site.net/dir/about.txt"

    res_relative_parent = base.resolve("../nexlog/")
    assert res_relative_parent == "nex://my-site.net/nexlog/"
