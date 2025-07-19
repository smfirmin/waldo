import pytest
from pydantic import ValidationError
from app.models.data_models import LocationData, ArticleRequest, ArticleResponse


class TestLocationData:
    def test_location_data_valid(self):
        location = LocationData(
            name="New York City",
            latitude=40.7128,
            longitude=-74.0060,
            events_summary="Major events happened here.",
        )

        assert location.name == "New York City"
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        assert location.events_summary == "Major events happened here."

    def test_location_data_optional_summary(self):
        location = LocationData(name="Paris", latitude=48.8566, longitude=2.3522)

        assert location.events_summary is None

    def test_location_data_invalid_coordinates(self):
        with pytest.raises(ValidationError):
            LocationData(name="Invalid", latitude="not_a_number", longitude=-74.0060)


class TestArticleRequest:
    def test_article_request_valid_url(self):
        request = ArticleRequest(input="https://example.com/article")
        assert request.input == "https://example.com/article"
        assert request.is_url() is True
        assert request.get_url() == "https://example.com/article"

    def test_article_request_valid_text(self):
        text = "This is some article text content"
        request = ArticleRequest(input=text)
        assert request.input == text
        assert request.is_url() is False
        assert request.get_text() == text

    def test_article_request_empty_input(self):
        with pytest.raises(ValidationError):
            ArticleRequest(input="")

    def test_article_request_whitespace_input(self):
        with pytest.raises(ValidationError):
            ArticleRequest(input="   ")

    def test_article_request_url_detection_various_formats(self):
        # Test various URL formats (excluding blocked ones)
        urls = [
            "https://example.com",
            "http://example.com/path",
            "https://sub.example.com/path?query=value",
            "https://news.bbc.co.uk/article",
        ]

        for url in urls:
            request = ArticleRequest(input=url)
            assert request.is_url() is True

    def test_article_request_blocked_urls(self):
        # Test that security-sensitive URLs are blocked
        blocked_urls = [
            "http://localhost:8080",
            "https://192.168.1.1:3000/api",
            "http://127.0.0.1/admin",
            "https://10.0.0.1/secret",
        ]

        for url in blocked_urls:
            with pytest.raises(
                ValidationError, match="URL not allowed for security reasons"
            ):
                ArticleRequest(input=url)

    def test_article_request_input_too_large(self):
        # Test that very large inputs are rejected
        large_input = "x" * 100001  # Just over 100KB limit
        with pytest.raises(ValidationError, match="Input too large"):
            ArticleRequest(input=large_input)

    def test_article_request_text_detection(self):
        # Test various text inputs that should not be detected as URLs
        texts = [
            "This is regular article text",
            "example.com without protocol",
            "Just some words and sentences",
            "https://incomplete",
            "Multiple sentences. This should be treated as text.",
        ]

        for text in texts:
            request = ArticleRequest(input=text)
            assert request.is_url() is False

    def test_get_url_from_text_input_raises_error(self):
        request = ArticleRequest(input="This is text, not a URL")
        with pytest.raises(ValueError, match="Input is not a valid URL"):
            request.get_url()

    def test_get_text_from_url_input_raises_error(self):
        request = ArticleRequest(input="https://example.com")
        with pytest.raises(ValueError, match="Cannot get text from URL"):
            request.get_text()


class TestArticleResponse:
    def test_article_response_complete(self):
        locations = [
            LocationData(name="NYC", latitude=40.7128, longitude=-74.0060),
            LocationData(name="Paris", latitude=48.8566, longitude=2.3522),
        ]

        response = ArticleResponse(
            article_title="Test Article",
            article_text="This is the article text.",
            locations=locations,
            processing_time=1.5,
        )

        assert response.article_title == "Test Article"
        assert response.article_text == "This is the article text."
        assert len(response.locations) == 2
        assert response.processing_time == 1.5

    def test_article_response_optional_title(self):
        response = ArticleResponse(
            article_text="Article text", locations=[], processing_time=0.5
        )

        assert response.article_title is None
        assert response.article_text == "Article text"
        assert response.locations == []
