from unittest.mock import Mock, patch
from app.services.location_extractor import LocationExtractor


class TestLocationExtractor:
    def setup_method(self):
        self.extractor = LocationExtractor("fake-api-key")

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_success(self, mock_model_class):
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["New York City", "Central Park", "Manhattan"]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # Create new extractor to use mocked model
        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations(
            "Article about New York City and Central Park"
        )

        assert locations == ["New York City", "Central Park", "Manhattan"]
        mock_model.generate_content.assert_called_once()

    @patch("app.services.location_extractor.genai.GenerativeModel")
    def test_extract_locations_with_extra_text(self, mock_model_class):
        # Mock response with extra text around JSON
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = (
            'Here are the locations: ["Paris", "London"] from the article.'
        )
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        assert locations == ["Paris", "London"]

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
    def test_extract_locations_filters_non_strings(self, mock_model_class):
        # Mock response with mixed data types
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["Valid Location", 123, "", "Another Location", null]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        extractor = LocationExtractor("fake-api-key")
        locations = extractor.extract_locations("Article text")

        assert locations == ["Valid Location", "Another Location"]
