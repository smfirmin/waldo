import pytest
from unittest.mock import Mock, patch
import requests
from app.services.article_extractor import ArticleExtractor


class TestArticleExtractor:
    def setup_method(self):
        self.extractor = ArticleExtractor()

    @patch("app.services.article_extractor.requests.get")
    def test_extract_from_url_success(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <p>This is a test article about New York City.</p>
                    <p>The event happened in Central Park.</p>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        title, text = self.extractor.extract_from_url("https://example.com/article")

        assert title == "Test Article"
        assert "This is a test article about New York City" in text
        assert "The event happened in Central Park" in text
        mock_get.assert_called_once()

    @patch("app.services.article_extractor.requests.get")
    def test_extract_from_url_no_article_tag(self, mock_get):
        # Mock response without article tag
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head><title>Test Title</title></head>
            <body>
                <div>Some content here</div>
                <p>More content in the body.</p>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        title, text = self.extractor.extract_from_url("https://example.com/article")

        assert title == "Test Title"
        assert "Some content here" in text
        assert "More content in the body" in text

    @patch("app.services.article_extractor.requests.get")
    def test_extract_from_url_request_failure(self, mock_get):
        # Mock request failure
        mock_get.side_effect = requests.RequestException("Connection error")

        with pytest.raises(Exception) as exc_info:
            self.extractor.extract_from_url("https://example.com/article")

        assert "Failed to extract article" in str(exc_info.value)

    @patch("app.services.article_extractor.requests.get")
    def test_extract_from_url_removes_scripts_and_styles(self, mock_get):
        # Mock response with script and style tags
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head><title>Test</title></head>
            <body>
                <script>console.log('hidden');</script>
                <style>body { color: red; }</style>
                <article>
                    <p>Visible content</p>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        title, text = self.extractor.extract_from_url("https://example.com/article")

        assert "Visible content" in text
        assert "console.log" not in text
        assert "color: red" not in text
