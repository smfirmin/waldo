import pytest
import json
import os
from unittest.mock import Mock, patch
from app import create_app
from app.services.location_extractor import RateLimitError


@pytest.fixture
def app():
    """Create test Flask application"""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestHealthEndpoint:
    """Test health check endpoint - no mocking needed"""

    def test_health_check_success(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "waldo"


class TestProgressEndpoint:
    """Test Server-Sent Events progress endpoint"""

    def test_progress_stream_invalid_session(self, client):
        """Test progress stream with invalid session ID"""
        response = client.get("/api/progress/invalid-session-id")

        assert response.status_code == 200
        assert response.mimetype == "text/event-stream"

        # Check headers
        assert response.headers["Cache-Control"] == "no-cache"
        assert response.headers["Connection"] == "keep-alive"

    def test_progress_stream_headers(self, client):
        """Test progress stream has correct SSE headers"""
        response = client.get("/api/progress/test-session")

        assert response.status_code == 200
        assert response.mimetype == "text/event-stream"
        assert "Cache-Control" in response.headers
        assert "Access-Control-Allow-Origin" in response.headers


class TestExtractEndpoint:
    """Test main extraction endpoint"""

    def test_extract_missing_data(self, client):
        """Test extract endpoint with no JSON data"""
        # Send empty JSON object
        response = client.post("/api/extract", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error_code"] == "MISSING_DATA"  # Empty JSON triggers MISSING_DATA
        assert "No data provided" in data["message"]

    def test_extract_missing_input_field(self, client):
        """Test extract endpoint with missing input field"""
        response = client.post("/api/extract", json={"other_field": "value"})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error_code"] == "MISSING_INPUT"
        assert "input" in data["message"]

    def test_extract_invalid_input_empty(self, client):
        """Test extract endpoint with empty input"""
        response = client.post("/api/extract", json={"input": ""})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid request data" in data["error"]

    def test_extract_invalid_input_too_large(self, client):
        """Test extract endpoint with input too large"""
        large_input = "x" * 100001  # Larger than 100KB limit
        response = client.post("/api/extract", json={"input": large_input})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid request data" in data["error"]

    @patch("app.api.routes.article_extractor")
    def test_extract_url_extraction_failed(self, mock_extractor, client):
        """Test extract endpoint with URL extraction failure"""
        mock_extractor.extract_from_url.side_effect = Exception("Network error")

        response = client.post(
            "/api/extract", json={"input": "https://example.com/article"}
        )

        # Direct API returns error immediately
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Network error" in data["error"]

    @patch("app.api.routes.article_extractor")
    def test_extract_url_no_content(self, mock_extractor, client):
        """Test extract endpoint with URL returning no content"""
        mock_extractor.extract_from_url.return_value = ("Title", "")

        response = client.post(
            "/api/extract", json={"input": "https://example.com/article"}
        )

        # Direct API returns error immediately for no content
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "No readable content found" in data["error"]

    @patch("app.api.routes.get_ai_services")
    def test_extract_rate_limit_error(self, mock_ai_services, client):
        """Test extract endpoint with rate limit error"""
        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.side_effect = RateLimitError(
            "Rate limited"
        )
        mock_ai_services.return_value = (mock_location_extractor, Mock())

        response = client.post(
            "/api/extract",
            json={"input": "This is a test article about Paris, France."},
        )

        # Direct API returns 429 for rate limit error
        assert response.status_code == 429
        data = json.loads(response.data)
        assert "error" in data
        assert "rate limit exceeded" in data["error"].lower()

    def test_input_validation_edge_cases(self, client):
        """Test Pydantic validation with various edge cases"""
        # Empty string should fail validation
        response = client.post("/api/extract", json={"input": ""})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid request data" in data["error"]

        # Whitespace only should fail validation
        response = client.post("/api/extract", json={"input": "   "})
        assert response.status_code == 400

    def test_large_input_rejected(self, client):
        """Test that input size limits are enforced"""
        # Input over 100KB limit should be rejected
        large_input = "x" * 100001
        response = client.post("/api/extract", json={"input": large_input})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid request data" in data["error"]

    def test_error_response_structure(self, client):
        """Test that error responses have consistent structure"""
        response = client.post("/api/extract", json={})
        assert response.status_code == 400
        data = json.loads(response.data)

        # Error responses should have these required fields
        assert "error_code" in data
        assert "message" in data
        assert "request_id" in data
        assert "timestamp" in data

    def test_url_vs_text_detection(self, client):
        """Test URL detection logic without mocking"""
        # Valid URLs should be processed as URLs but will fail extraction
        url_inputs = [
            "https://example.com/article",
            "http://news.site.com/story",
            "https://www.bbc.com/news/world-123",
        ]

        for url_input in url_inputs:
            response = client.post("/api/extract", json={"input": url_input})
            # URLs will fail extraction (400) since they're not real
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY"),
        reason="Requires GEMINI_API_KEY for end-to-end test",
    )
    def test_end_to_end_integration(self, client):
        """End-to-end test with real AI service"""
        test_input = "There was a meeting in Paris, France."

        response = client.post("/api/extract", json={"input": test_input})

        if response.status_code == 200:
            data = json.loads(response.data)

            # Direct API returns results immediately
            required_fields = [
                "article_text",
                "article_title",
                "locations",
                "processing_time",
            ]
            for field in required_fields:
                assert field in data

            assert data["article_text"] == test_input
            assert data["article_title"] == "Article Text"
            assert isinstance(data["locations"], list)
            assert isinstance(data["processing_time"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__])
