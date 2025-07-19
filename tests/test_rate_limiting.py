import pytest
import json
from unittest.mock import Mock, patch
from app import create_app
from app.services.location_extractor import RateLimitError


@pytest.fixture
def app():
    """Create test Flask app"""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestRateLimitHandling:
    @patch("app.api.routes.get_ai_services")
    @patch("app.api.routes.article_extractor")
    def test_rate_limit_error_handling(self, mock_extractor, mock_ai_services, client):
        """Test that rate limit errors are handled gracefully"""
        # Mock article extractor
        mock_extractor.extract_from_url.return_value = (
            "Test Article",
            "This is test content with locations.",
        )

        # Mock AI services to raise rate limit error
        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.side_effect = RateLimitError(
            "API rate limit exceeded. Please try again in a few moments."
        )
        mock_ai_services.return_value = (mock_location_extractor, Mock())

        # Make request
        response = client.post(
            "/api/extract",
            json={"input": "https://example.com/article"},
            content_type="application/json",
        )

        assert response.status_code == 429
        data = json.loads(response.data)

        assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert "rate limit exceeded" in data["message"].lower()
        assert data["retry_after"] == 60
        assert response.headers.get("Retry-After") == "60"

    @patch("app.api.routes.get_ai_services")
    def test_rate_limit_error_from_text_input(self, mock_ai_services, client):
        """Test rate limit handling with text input"""
        # Mock AI services to raise rate limit error
        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.side_effect = RateLimitError(
            "Quota exceeded"
        )
        mock_ai_services.return_value = (mock_location_extractor, Mock())

        # Make request with text input
        response = client.post(
            "/api/extract",
            json={"input": "This is some article text mentioning New York."},
            content_type="application/json",
        )

        assert response.status_code == 429
        data = json.loads(response.data)
        assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
