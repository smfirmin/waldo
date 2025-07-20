import pytest
import json
from unittest.mock import Mock, patch
from app import create_app
from app.models.data_models import ExtractedLocation, LocationData
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
    """Test health check endpoint"""

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

    @patch("app.api.routes.get_progress_tracker")
    def test_extract_missing_input_field(self, mock_tracker_factory, client):
        """Test extract endpoint with missing input field"""
        mock_tracker = Mock()
        mock_tracker_factory.return_value = mock_tracker

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

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["error_code"] == "URL_EXTRACTION_FAILED"
        assert "Network error" in data["details"]

    @patch("app.api.routes.article_extractor")
    def test_extract_url_no_content(self, mock_extractor, client):
        """Test extract endpoint with URL returning no content"""
        mock_extractor.extract_from_url.return_value = ("Title", "")

        response = client.post(
            "/api/extract", json={"input": "https://example.com/article"}
        )

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["error_code"] == "NO_CONTENT"
        assert "No readable content" in data["message"]

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

        assert response.status_code == 429
        data = json.loads(response.data)
        assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert "rate limit" in data["message"].lower()
        assert data["retry_after"] == 60

    @patch("app.api.routes.get_ai_services")
    @patch("app.api.routes.location_processor")
    def test_extract_success_no_locations(
        self, mock_processor, mock_ai_services, client
    ):
        """Test successful extraction with no locations found"""
        # Setup mocks
        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.return_value = []
        mock_ai_services.return_value = (mock_location_extractor, Mock())

        response = client.post(
            "/api/extract", json={"input": "This is a test article with no locations."}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["article_title"] == "Article Text"
        assert data["locations"] == []
        assert data["request_id"]  # This should exist in the response
        assert data["processing_time"] > 0
        # Note: session_id is not added for early returns, only for the final response

    @patch("app.api.routes.get_ai_services")
    @patch("app.api.routes.location_processor")
    def test_extract_success_with_locations(
        self, mock_processor, mock_ai_services, client
    ):
        """Test successful extraction with locations found"""
        # Setup mock extracted locations
        extracted_locations = [
            ExtractedLocation(
                original_text="Paris",
                standardized_name="Paris, France",
                context="mentioned in article",
                confidence="high",
                location_type="city",
                disambiguation_hints=["France"],
            )
        ]

        # Setup mock processed locations
        processed_locations = [
            LocationData(
                name="Paris, France",
                latitude=48.8566,
                longitude=2.3522,
                events_summary="Events in Paris",
                confidence=0.9,
                resolution_method="direct",
                original_text="Paris",
            )
        ]

        # Setup mocks
        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.return_value = extracted_locations
        mock_summarizer = Mock()
        mock_ai_services.return_value = (mock_location_extractor, mock_summarizer)

        mock_processor.process_locations_pipeline.return_value = (
            processed_locations,
            [],
        )
        mock_processor.apply_spatial_filtering.return_value = processed_locations

        response = client.post(
            "/api/extract", json={"input": "This is an article about Paris, France."}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["article_title"] == "Article Text"
        assert len(data["locations"]) == 1
        assert data["locations"][0]["name"] == "Paris, France"
        assert data["locations"][0]["latitude"] == 48.8566
        assert data["locations"][0]["longitude"] == 2.3522
        assert "session_id" in data
        assert data["processing_time"] > 0

    @patch("app.api.routes.article_extractor")
    @patch("app.api.routes.get_ai_services")
    @patch("app.api.routes.location_processor")
    def test_extract_success_with_url(
        self, mock_processor, mock_ai_services, mock_extractor, client
    ):
        """Test successful extraction from URL"""
        # Setup URL extraction mock
        mock_extractor.extract_from_url.return_value = (
            "Article Title",
            "Article content about Tokyo, Japan.",
        )

        # Setup AI services mock
        extracted_locations = [
            ExtractedLocation(
                original_text="Tokyo",
                standardized_name="Tokyo, Japan",
                context="mentioned in article",
                confidence="high",
                location_type="city",
                disambiguation_hints=["Japan"],
            )
        ]

        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.return_value = extracted_locations
        mock_ai_services.return_value = (mock_location_extractor, Mock())

        # Setup location processor mock
        mock_processor.process_locations_pipeline.return_value = ([], [])
        mock_processor.apply_spatial_filtering.return_value = []

        response = client.post(
            "/api/extract", json={"input": "https://example.com/tokyo-article"}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["article_title"] == "Article Title"
        assert "tokyo" in data["article_text"].lower()
        assert "session_id" in data

        # Verify URL extraction was called
        mock_extractor.extract_from_url.assert_called_once_with(
            "https://example.com/tokyo-article"
        )

    @patch("app.api.routes.get_ai_services")
    @patch("app.api.routes.location_processor")
    def test_extract_text_truncation_warning(
        self, mock_processor, mock_ai_services, client
    ):
        """Test that long text gets truncated with warning"""
        # Create text longer than 50KB limit
        long_text = "x" * 50001

        # Setup mocks to simulate finding locations so we get the full response
        extracted_locations = [
            ExtractedLocation(
                original_text="test",
                standardized_name="Test Location",
                context="test",
                confidence="high",
                location_type="city",
                disambiguation_hints=[],
            )
        ]

        processed_locations = [
            LocationData(
                name="Test Location",
                latitude=0.0,
                longitude=0.0,
                events_summary="Test",
                confidence=0.9,
                resolution_method="direct",
                original_text="test",
            )
        ]

        mock_location_extractor = Mock()
        mock_location_extractor.extract_locations.return_value = extracted_locations
        mock_summarizer = Mock()
        mock_ai_services.return_value = (mock_location_extractor, mock_summarizer)

        mock_processor.process_locations_pipeline.return_value = (
            processed_locations,
            [],
        )
        mock_processor.apply_spatial_filtering.return_value = processed_locations

        response = client.post("/api/extract", json={"input": long_text})

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check for truncation warning
        assert len(data["warnings"]) > 0
        assert any("TEXT_TRUNCATED" in warning["code"] for warning in data["warnings"])

        # Verify text was actually truncated
        assert len(data["article_text"]) == 50000

    def test_extract_progress_tracking_integration(self, client):
        """Test that progress tracking is properly integrated"""
        with patch("app.api.routes.get_progress_tracker") as mock_tracker_factory:
            mock_tracker = Mock()
            mock_tracker_factory.return_value = mock_tracker

            with patch("app.api.routes.get_ai_services") as mock_ai_services:
                mock_location_extractor = Mock()
                mock_location_extractor.extract_locations.return_value = []
                mock_ai_services.return_value = (mock_location_extractor, Mock())

                response = client.post("/api/extract", json={"input": "Test article"})

                assert response.status_code == 200

                # Verify progress tracker methods were called
                mock_tracker.start_processing.assert_called_once()
                mock_tracker.start_article_extraction.assert_called_once_with(
                    "Test article"
                )
                mock_tracker.start_location_extraction.assert_called_once()
                mock_tracker.locations_found.assert_called_once_with(0)
                mock_tracker.complete.assert_called_once()


class TestProgressTrackerIntegration:
    """Test progress tracker integration with API routes"""

    def test_progress_tracker_error_handling(self, client):
        """Test progress tracker handles errors properly"""
        # Test missing data error - progress tracker should handle gracefully
        response = client.post("/api/extract", json={})
        assert response.status_code == 400

        # Test missing input error
        response = client.post("/api/extract", json={"other": "value"})
        assert response.status_code == 400

    @patch("app.api.routes.get_progress_tracker")
    @patch("app.api.routes.article_extractor")
    def test_progress_tracker_url_extraction_error(
        self, mock_extractor, mock_tracker_factory, client
    ):
        """Test progress tracker handles URL extraction errors"""
        mock_tracker = Mock()
        mock_tracker_factory.return_value = mock_tracker
        mock_extractor.extract_from_url.side_effect = Exception("Network error")

        response = client.post("/api/extract", json={"input": "https://example.com"})

        assert response.status_code == 422
        mock_tracker.error.assert_called_once()
        error_call = mock_tracker.error.call_args[0][0]
        assert "Network error" in error_call


if __name__ == "__main__":
    pytest.main([__file__])
