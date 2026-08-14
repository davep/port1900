import dataclasses

import pytest

from port1900.response import Response
from port1900.uri import NexURI


def test_response_utf8() -> None:
    uri = NexURI("nex://example.com/file.txt")
    raw = b"Hello, Nex!\nLine 2"
    resp = Response(uri=uri, raw_bytes=raw)

    assert resp.content == raw
    assert resp.text == "Hello, Nex!\nLine 2"
    assert resp.lines == ["Hello, Nex!", "Line 2"]
    assert not resp.is_directory
    assert repr(resp) == f"<Response [URI: {uri}] {len(raw)} bytes>"


def test_response_iso8859_fallback() -> None:
    uri = NexURI("nex://example.com/file.txt")
    # Invalid UTF-8 bytes, but valid ISO-8859-1 (Latin-1) string ("café")
    raw_latin1 = b"caf\xe9"

    resp = Response(uri=uri, raw_bytes=raw_latin1, encoding="utf-8")
    # UTF-8 decode will fail, falling back to iso8859-1
    assert resp.text == "café"


def test_response_replace_fallback() -> None:
    uri = NexURI("nex://example.com/file.txt")
    raw_bad = b"hello \xff\xfe world"

    resp = Response(uri=uri, raw_bytes=raw_bad)
    assert isinstance(resp.text, str)


def test_response_directory_flag() -> None:
    uri_dir = NexURI("nex://example.com/docs/")
    resp_dir = Response(uri=uri_dir, raw_bytes=b"=> file.txt\n")
    assert resp_dir.is_directory


def test_response_mime_type() -> None:
    txt_resp = Response(uri=NexURI("nex://example.com/file.txt"), raw_bytes=b"text")
    assert txt_resp.mime_type == "text/plain"

    html_resp = Response(
        uri=NexURI("nex://example.com/index.html"), raw_bytes=b"<h1>Hi</h1>"
    )
    assert html_resp.mime_type == "text/html"

    png_resp = Response(uri=NexURI("nex://example.com/photo.png"), raw_bytes=b"\x89PNG")
    assert png_resp.mime_type == "image/png"

    # Fallback to text/plain when no extension or unknown extension
    no_ext_resp = Response(uri=NexURI("nex://example.com/hello"), raw_bytes=b"hello")
    assert no_ext_resp.mime_type == "text/plain"

    dir_resp = Response(uri=NexURI("nex://example.com/dir/"), raw_bytes=b"=> a.txt\n")
    assert dir_resp.mime_type == "text/plain"


def test_response_frozen_and_hashable() -> None:
    uri = NexURI("nex://example.com/file.txt")
    resp = Response(uri=uri, raw_bytes=b"hello")

    with pytest.raises(dataclasses.FrozenInstanceError):
        resp.raw_bytes = b"modified"  # type: ignore[misc]

    with pytest.raises(dataclasses.FrozenInstanceError):
        resp.encoding = "latin-1"  # type: ignore[misc]

    assert isinstance(hash(resp), int)
    assert {resp} == {resp}


def test_response_cached_properties() -> None:
    uri = NexURI("nex://example.com/file.txt")
    resp = Response(uri=uri, raw_bytes=b"line 1\nline 2")

    # text, lines, and mime_type are cached properties
    assert resp.text is resp.text
    assert resp.lines is resp.lines
    assert resp.mime_type is resp.mime_type
