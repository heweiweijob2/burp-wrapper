"""Tests for custom exceptions."""

import pytest

from burp_wrapper.exceptions import (
    BurpAPIError,
    BurpConnectionError,
    BurpWrapperError,
    NotImplementedInBurpMCP,
    SessionError,
)


class TestExceptionHierarchy:
    def test_api_error_is_wrapper_error(self):
        assert issubclass(BurpAPIError, BurpWrapperError)

    def test_connection_error_is_wrapper_error(self):
        assert issubclass(BurpConnectionError, BurpWrapperError)

    def test_not_implemented_is_wrapper_error(self):
        assert issubclass(NotImplementedInBurpMCP, BurpWrapperError)

    def test_session_error_is_wrapper_error(self):
        assert issubclass(SessionError, BurpWrapperError)


class TestBurpAPIError:
    def test_stores_code_and_message(self):
        err = BurpAPIError(code=404, message="Not found")
        assert err.code == 404
        assert err.message == "Not found"

    def test_str_includes_code(self):
        err = BurpAPIError(code=500, message="Server error")
        assert "[500]" in str(err)
        assert "Server error" in str(err)

    def test_default_values(self):
        err = BurpAPIError()
        assert err.code == -1
        assert err.message == "Unknown error"


class TestNotImplementedInBurpMCP:
    def test_can_raise_with_message(self):
        with pytest.raises(NotImplementedInBurpMCP, match="scanner.crawl"):
            raise NotImplementedInBurpMCP("scanner.crawl is not supported")
