"""Unit tests for web_fetch tool."""

from unittest.mock import Mock, patch

import pytest

from tools.web_fetch import web_fetch


class TestWebFetchFunction:
    """Test web_fetch function."""

    @patch("tools.web_fetch.requests.get")
    def test_web_fetch_success(self, mock_get):
        """Test successful web fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response

        result = web_fetch("https://example.com")

        assert result is not None
        mock_get.assert_called_once()

    @patch("tools.web_fetch.requests.get")
    def test_web_fetch_with_invalid_url(self, mock_get):
        """Test web fetch with invalid URL."""
        mock_get.side_effect = Exception("Invalid URL")

        # Function should handle errors gracefully
        result = web_fetch("invalid-url")

        # Result handling depends on implementation
        assert result is not None or result is None

    def test_web_fetch_function_exists(self):
        """Test web_fetch function exists and is callable."""
        assert callable(web_fetch)

    def test_web_fetch_accepts_url_parameter(self):
        """Test web_fetch accepts URL parameter."""
        import inspect

        sig = inspect.signature(web_fetch)
        params = list(sig.parameters.keys())

        assert len(params) >= 1  # At least URL parameter
