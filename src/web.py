"""Web request and JSON utilities for the E language.

Provides HTTP GET/POST requests and JSON parsing/handling using only
the Python standard library (urllib + json).

Usage from the interpreter:
    result = http_get("https://api.example.com/data")
    result = http_get("https://api.example.com/data", timeout=5)
    result = http_post("https://api.example.com/data", '{"key": "val"}')
    result = http_post("https://api.example.com/data", '{"key": "val"}', timeout=5)
    parsed = json_parse('{"key": "value"}')
    converted = json_of(parsed)  # back to JSON string
    keys = json_keys(parsed)
    val = json_value(parsed, "key")
"""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from typing import Any, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


DEFAULT_TIMEOUT = 10  # seconds


@dataclass
class HttpResult:
    """A simple HTTP response wrapper."""
    status: int
    body: str


def http_get(url: str, timeout: int = DEFAULT_TIMEOUT) -> HttpResult:
    """Perform an HTTP GET request. Returns an HttpResult."""
    try:
        req = Request(url, method="GET")
        req.add_header("User-Agent", "E-Language/0.4")
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return HttpResult(status=resp.status, body=body)
    except HTTPError as e:
        # Server returned an error status (4xx, 5xx) — still return the response
        body = ""
        if e.fp is not None:
            try:
                body = e.fp.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return HttpResult(status=e.code, body=body)
    except URLError as e:
        raise RuntimeError(
            f"I couldn't reach the server: {e.reason}"
        )
    except TimeoutError:
        raise RuntimeError(
            f"I couldn't reach the server: the request timed out after {timeout} seconds"
        )
    except Exception as e:
        raise RuntimeError(
            f"I couldn't reach the server: {e}"
        )


def http_post(url: str, body: str = "", timeout: int = DEFAULT_TIMEOUT) -> HttpResult:
    """Perform an HTTP POST request. Returns an HttpResult."""
    data = body.encode("utf-8") if body else None
    try:
        req = Request(url, data=data, method="POST")
        req.add_header("User-Agent", "E-Language/0.4")
        if body:
            req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            return HttpResult(status=resp.status, body=resp_body)
    except HTTPError as e:
        resp_body = ""
        if e.fp is not None:
            try:
                resp_body = e.fp.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return HttpResult(status=e.code, body=resp_body)
    except URLError as e:
        raise RuntimeError(
            f"I couldn't reach the server: {e.reason}"
        )
    except TimeoutError:
        raise RuntimeError(
            f"I couldn't reach the server: the request timed out after {timeout} seconds"
        )
    except Exception as e:
        raise RuntimeError(
            f"I couldn't reach the server: {e}"
        )


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def json_parse(text: str) -> Any:
    """Parse a JSON string into E data structures.

    - JSON objects  → list of [key, value] pairs: [["name", "Alice"], ["age", 30]]
    - JSON arrays   → Python lists
    - JSON strings  → Python strings
    - JSON numbers  → Python int or float
    - JSON booleans → Python bool
    - JSON null     → None
    """
    try:
        raw = _json.loads(text)
    except _json.JSONDecodeError as e:
        raise RuntimeError(
            f"I couldn't read the JSON: {e.msg} (line {e.lineno}, column {e.colno})"
        )
    return _to_e_value(raw)


def _to_e_value(obj: Any) -> Any:
    """Recursively convert a Python object (from json.loads) to E-friendly values."""
    if isinstance(obj, dict):
        # JSON object → list of [key, value] pairs
        return [[str(k), _to_e_value(v)] for k, v in obj.items()]
    if isinstance(obj, list):
        return [_to_e_value(item) for item in obj]
    # primitives pass through (str, int, float, bool, None)
    return obj


def json_of(value: Any) -> str:
    """Convert a value to a JSON string.

    - If given an HttpResult, parses its body as JSON and re-serializes.
    - If given a list (E data structure), converts back to JSON.
    - If given a string, tries to parse it as JSON, then re-serializes.
    """
    if isinstance(value, HttpResult):
        # Parse the response body, then dump back to JSON
        raw = _json.loads(value.body)
        return _json.dumps(raw, ensure_ascii=False, indent=2)
    if isinstance(value, str):
        # Try to parse as JSON, then re-serialize for pretty output
        try:
            raw = _json.loads(value)
            return _json.dumps(raw, ensure_ascii=False, indent=2)
        except _json.JSONDecodeError:
            # Not JSON — just return the string as a JSON-encoded string
            return _json.dumps(value, ensure_ascii=False)
    # list, dict, int, float, bool, None — convert to JSON
    py_val = _from_e_value(value)
    return _json.dumps(py_val, ensure_ascii=False, indent=2)


def _from_e_value(obj: Any) -> Any:
    """Convert E data structures back to Python objects for json.dumps."""
    if isinstance(obj, list):
        # Check if it's a list-of-pairs (each element is a 2-element list)
        if obj and isinstance(obj[0], list) and len(obj[0]) == 2:
            # Convert list-of-pairs back to dict
            return {str(pair[0]): _from_e_value(pair[1]) for pair in obj}
        return [_from_e_value(item) for item in obj]
    return obj


def json_keys(obj: Any) -> List[str]:
    """Get the keys of a JSON object (list-of-pairs)."""
    if not isinstance(obj, list):
        raise RuntimeError(
            "json keys needs a JSON object (a list of pairs), but I got something else."
        )
    if obj and isinstance(obj[0], list) and len(obj[0]) == 2:
        return [str(pair[0]) for pair in obj]
    raise RuntimeError(
        "json keys needs a JSON object (a list of pairs), but I got a plain list."
    )


def json_value(obj: Any, key: str) -> Any:
    """Get a value from a JSON object (list-of-pairs) by key."""
    if not isinstance(obj, list):
        raise RuntimeError(
            "json value needs a JSON object (a list of pairs), but I got something else."
        )
    if not isinstance(key, str):
        raise RuntimeError(
            f"json value needs a key (text), but I got {type(key).__name__}."
        )
    for pair in obj:
        if isinstance(pair, list) and len(pair) == 2 and pair[0] == key:
            return pair[1]
    raise RuntimeError(
        f"I couldn't find the key \"{key}\" in the JSON object."
    )
