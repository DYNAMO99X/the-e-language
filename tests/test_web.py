"""Tests for the web request and JSON builtins.

All HTTP tests use mocked urllib — no real network calls.
"""

from __future__ import annotations
import io
import json
import unittest
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout

from src.interpreter import Interpreter
from src.web import (
    http_get, http_post, json_parse, json_of, json_keys, json_value,
    HttpResult, DEFAULT_TIMEOUT,
)


def run(src: str) -> Interpreter:
    """Run E source and return the Interpreter."""
    interp = Interpreter("<web-test>", turtle_mode="text")
    buf = io.StringIO()
    with redirect_stdout(buf):
        interp.run_string(src)
    return interp


def _mock_response(status=200, body='{"key": "value"}'):
    """Create a mock urllib response object."""
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    resp.read.return_value = body.encode("utf-8")
    return resp


# ---------------------------------------------------------------------------
# Unit tests for src/web.py (direct Python calls)
# ---------------------------------------------------------------------------

class TestHttpResult(unittest.TestCase):
    def test_creation(self):
        r = HttpResult(status=200, body="hello")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, "hello")


class TestJsonParse(unittest.TestCase):
    def test_parse_object(self):
        result = json_parse('{"name": "Alice", "age": 30}')
        self.assertEqual(result, [["name", "Alice"], ["age", 30]])

    def test_parse_array(self):
        result = json_parse('[1, 2, 3]')
        self.assertEqual(result, [1, 2, 3])

    def test_parse_string(self):
        result = json_parse('"hello"')
        self.assertEqual(result, "hello")

    def test_parse_number(self):
        result = json_parse('42')
        self.assertEqual(result, 42)

    def test_parse_nested(self):
        result = json_parse('{"a": {"b": 1}}')
        self.assertEqual(result, [["a", [["b", 1]]]])

    def test_parse_bad_json(self):
        with self.assertRaises(RuntimeError) as cm:
            json_parse("{bad json}")
        self.assertIn("couldn't read the JSON", str(cm.exception))


class TestJsonOf(unittest.TestCase):
    def test_roundtrip(self):
        obj = json_parse('{"name": "Alice"}')
        text = json_of(obj)
        reloaded = json.loads(text)
        self.assertEqual(reloaded, {"name": "Alice"})

    def test_from_string(self):
        result = json_of('{"a": 1}')
        self.assertEqual(json.loads(result), {"a": 1})

    def test_from_list(self):
        result = json_of([1, 2, 3])
        self.assertEqual(json.loads(result), [1, 2, 3])


class TestJsonKeys(unittest.TestCase):
    def test_keys(self):
        obj = json_parse('{"name": "Alice", "age": 30}')
        keys = json_keys(obj)
        self.assertEqual(keys, ["name", "age"])

    def test_keys_not_object(self):
        with self.assertRaises(RuntimeError):
            json_keys([1, 2, 3])


class TestJsonValue(unittest.TestCase):
    def test_value(self):
        obj = json_parse('{"name": "Alice", "age": 30}')
        self.assertEqual(json_value(obj, "name"), "Alice")
        self.assertEqual(json_value(obj, "age"), 30)

    def test_value_missing_key(self):
        obj = json_parse('{"name": "Alice"}')
        with self.assertRaises(RuntimeError) as cm:
            json_value(obj, "missing")
        self.assertIn("couldn't find the key", str(cm.exception))

    def test_value_wrong_type(self):
        with self.assertRaises(RuntimeError):
            json_value("not a list", "key")


class TestHttpGet(unittest.TestCase):
    @patch("src.web.urlopen")
    def test_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, '{"ok": true}')
        result = http_get("https://example.com/api")
        self.assertEqual(result.status, 200)
        self.assertIn("ok", result.body)

    @patch("src.web.urlopen")
    def test_404(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(404, "not found")
        result = http_get("https://example.com/missing")
        self.assertEqual(result.status, 404)

    @patch("src.web.urlopen")
    def test_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")
        with self.assertRaises(RuntimeError) as cm:
            http_get("https://example.com/slow", timeout=5)
        self.assertIn("timed out", str(cm.exception))

    @patch("src.web.urlopen")
    def test_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Name or service not known")
        with self.assertRaises(RuntimeError) as cm:
            http_get("https://nonexistent.example.com")
        self.assertIn("couldn't reach the server", str(cm.exception))


class TestHttpPost(unittest.TestCase):
    @patch("src.web.urlopen")
    def test_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(201, '{"created": true}')
        result = http_post("https://example.com/api", '{"name": "Bob"}')
        self.assertEqual(result.status, 201)

    @patch("src.web.urlopen")
    def test_no_body(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, "ok")
        result = http_post("https://example.com/api")
        self.assertEqual(result.status, 200)


# ---------------------------------------------------------------------------
# Integration tests (run E source through the interpreter)
# ---------------------------------------------------------------------------

class TestWebInterpreterIntegration(unittest.TestCase):
    @patch("src.web.urlopen")
    def test_get_and_body_of(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, "hello world")
        interp = run('let resp be get "https://example.com"\nsay body of resp')
        self.assertIn("hello world", interp.output_buffer)

    @patch("src.web.urlopen")
    def test_get_and_status_of(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, "ok")
        interp = run('let resp be get "https://example.com"\nsay status of resp')
        self.assertIn("200", interp.output_buffer)

    @patch("src.web.urlopen")
    def test_post_and_body_of(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(201, "created")
        interp = run('let resp be post "https://example.com", `{"a":1}`\nsay body of resp')
        self.assertIn("created", interp.output_buffer)

    @patch("src.web.urlopen")
    def test_json_parse_and_keys(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, '{"name":"Alice","age":30}')
        interp = run(
            'let resp be get "https://example.com"\n'
            'let obj be json parse body of resp\n'
            'let keys be json keys obj\n'
            'say keys'
        )
        # E prints lists as [name, age] (no quotes on strings inside lists)
        output = interp.output_buffer[0] if interp.output_buffer else ""
        self.assertIn("name", output)
        self.assertIn("age", output)

    @patch("src.web.urlopen")
    def test_json_value(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, '{"name":"Bob"}')
        interp = run(
            'let resp be get "https://example.com"\n'
            'let obj be json parse body of resp\n'
            'say json value obj, "name"'
        )
        self.assertIn("Bob", interp.output_buffer)

    @patch("src.web.urlopen")
    def test_json_of_response(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(200, '{"x": 1}')
        interp = run(
            'let resp be get "https://example.com"\n'
            'let text be json of resp\n'
            'say text'
        )
        output = interp.output_buffer[0] if interp.output_buffer else ""
        self.assertIn("x", output)
        self.assertIn("1", output)

    @patch("src.web.urlopen")
    def test_network_error_message(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")
        with self.assertRaises(Exception) as cm:
            run('let resp be get "https://nonexistent.example.com"')
        self.assertIn("couldn't reach the server", str(cm.exception))

    @patch("src.web.urlopen")
    def test_timeout_in_e(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")
        with self.assertRaises(Exception) as cm:
            run('let resp be get "https://example.com", timeout 2')
        self.assertIn("timed out", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
