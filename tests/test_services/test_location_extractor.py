from unittest.mock import Mock, patch
from app.services.location_extractor import LocationExtractor
from app.models.data_models import ExtractedLocation


class TestLocationExtractor:
    def setup_method(self):
        self.extractor = LocationExtractor("fake-api-key")

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_success(self, mock_model_class):
        # Mock Gemini response with enhanced object format
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = """[
            {
                "original_text": "the Big Apple",
                "standardized_name": "New York City",
                "context": "tourism statistics mentioned",
                "confidence": "high",
                "location_type": "nickname",
                "disambiguation_hints": ["tourism", "visitors"]
            },
            {
                "original_text": "Paris",
                "standardized_name": "Paris",
                "context": "mentioned with Texas context",
                "confidence": "medium",
                "location_type": "city",
                "disambiguation_hints": ["Texas", "state"]
            }
        ]"""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations(
            "Article about the Big Apple and Paris, Texas"
        )

        assert len(locations) == 2

        # Check first location
        nyc = locations[0]
        assert isinstance(nyc, ExtractedLocation)
        assert nyc.original_text == "the Big Apple"
        assert nyc.standardized_name == "New York City"
        assert nyc.confidence == "high"
        assert nyc.location_type == "nickname"
        assert "tourism" in nyc.disambiguation_hints

        # Check second location
        paris = locations[1]
        assert isinstance(paris, ExtractedLocation)
        assert paris.original_text == "Paris"
        assert paris.standardized_name == "Paris"
        assert paris.confidence == "medium"
        assert "Texas" in paris.disambiguation_hints

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_string_format_triggers_correction(
        self, mock_model_class
    ):
        # Mock response with simple string array (should trigger self-correction)
        mock_model = Mock()
        mock_initial_response = Mock()
        mock_initial_response.text = '["New York City", "Central Park"]'

        # Mock corrected response
        mock_corrected_response = Mock()
        mock_corrected_response.text = """[
            {
                "original_text": "New York City",
                "standardized_name": "New York City",
                "context": "corrected by self-correction",
                "confidence": "medium",
                "location_type": "city",
                "disambiguation_hints": []
            }
        ]"""

        mock_model.generate_content.side_effect = [
            mock_initial_response,
            mock_corrected_response,
        ]
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        # Should get corrected response
        assert len(locations) == 1
        assert locations[0].standardized_name == "New York City"
        assert locations[0].context == "corrected by self-correction"

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_with_extra_text(self, mock_model_class):
        # Mock response with extra text around JSON
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = """Here are the locations: [
            {
                "original_text": "downtown",
                "standardized_name": "downtown Seattle", 
                "context": "mentioned with Seattle context",
                "confidence": "medium",
                "location_type": "generic",
                "disambiguation_hints": ["Seattle"]
            }
        ] from the article."""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        assert len(locations) == 1
        assert locations[0].original_text == "downtown"
        assert locations[0].standardized_name == "downtown Seattle"

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_invalid_json(self, mock_model_class):
        # Mock response with invalid JSON
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid response without JSON array"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        assert locations == []

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_api_error(self, mock_model_class):
        # Mock API error
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        assert locations == []

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_malformed_objects(self, mock_model_class):
        # Mock response with mix of valid and invalid objects
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = """[
            {
                "original_text": "Valid Location",
                "standardized_name": "Valid Location", 
                "context": "some context",
                "confidence": "high",
                "location_type": "city",
                "disambiguation_hints": []
            },
            {
                "missing_required_field": "invalid"
            },
            "fallback_string"
        ]"""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        # Should get only valid object, skip malformed object and string
        assert len(locations) == 1
        assert locations[0].original_text == "Valid Location"
