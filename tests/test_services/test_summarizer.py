from unittest.mock import Mock, patch
from app.services.summarizer import EventSummarizer


class TestEventSummarizer:
    def setup_method(self):
        self.summarizer = EventSummarizer("fake-api-key")

    @patch("app.services.summarizer.genai.GenerativeModel")
    def test_summarize_events_success(self, mock_model_class):
        # Mock successful summarization
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "A major protest took place in Central Park yesterday."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        summarizer = EventSummarizer("fake-api-key")
        summary = summarizer.summarize_events_at_location(
            "Article about protests in Central Park", "Central Park"
        )

        assert summary == "A major protest took place in Central Park yesterday."
        mock_model.generate_content.assert_called_once()

    @patch("app.services.summarizer.genai.GenerativeModel")
    def test_summarize_events_long_response_truncated(self, mock_model_class):
        # Mock long response that should be truncated
        mock_model = Mock()
        mock_response = Mock()
        long_text = "A" * 250  # Longer than 200 character limit
        mock_response.text = long_text
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        summarizer = EventSummarizer("fake-api-key")
        summary = summarizer.summarize_events_at_location("Article", "Location")

        assert len(summary) == 200  # 197 + "..."
        assert summary.endswith("...")

    @patch("app.services.summarizer.genai.GenerativeModel")
    def test_summarize_events_empty_response(self, mock_model_class):
        # Mock empty response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        summarizer = EventSummarizer("fake-api-key")
        summary = summarizer.summarize_events_at_location("Article", "Location")

        assert summary == "Mentioned in article."

    @patch("app.services.summarizer.genai.GenerativeModel")
    def test_summarize_events_api_error(self, mock_model_class):
        # Mock API error
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        summarizer = EventSummarizer("fake-api-key")
        summary = summarizer.summarize_events_at_location("Article", "Location")

        assert summary == "Mentioned in article."

    @patch("app.services.summarizer.genai.GenerativeModel")
    def test_summarize_events_whitespace_handling(self, mock_model_class):
        # Mock response with extra whitespace
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "  Events happened here.  \n\n  "
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        summarizer = EventSummarizer("fake-api-key")
        summary = summarizer.summarize_events_at_location("Article", "Location")

        assert summary == "Events happened here."
