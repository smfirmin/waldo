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
        request = ArticleRequest(url="https://example.com/article")
        assert str(request.url) == "https://example.com/article"

    def test_article_request_invalid_url(self):
        with pytest.raises(ValidationError):
            ArticleRequest(url="not_a_url")


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
