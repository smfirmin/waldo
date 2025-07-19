from unittest.mock import Mock, patch
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.services.geocoding import GeocodingService


class TestGeocodingService:
    def setup_method(self):
        self.service = GeocodingService()

    @patch("app.services.geocoding.Nominatim")
    def test_geocode_location_success(self, mock_nominatim_class):
        # Mock successful geocoding
        mock_geocoder = Mock()
        mock_location = Mock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        mock_location.raw = {
            "boundingbox": ["40.4774", "40.9176", "-74.2591", "-73.7004"],
            "class": "place",
            "type": "city",
            "address": {
                "city": "New York City",
                "state": "New York",
                "country": "United States",
            },
            "extratags": {"admin_level": "8"},
        }
        mock_geocoder.geocode.return_value = mock_location
        mock_nominatim_class.return_value = mock_geocoder

        service = GeocodingService()
        result = service.geocode_location("New York City")

        assert result == (40.7128, -74.0060)

    @patch("app.services.geocoding.Nominatim")
    def test_geocode_location_not_found(self, mock_nominatim_class):
        # Mock location not found
        mock_geocoder = Mock()
        mock_geocoder.geocode.return_value = None
        mock_nominatim_class.return_value = mock_geocoder

        service = GeocodingService()
        result = service.geocode_location("Nonexistent Place")

        assert result is None

    @patch("app.services.geocoding.Nominatim")
    def test_geocode_location_timeout(self, mock_nominatim_class):
        # Mock timeout error
        mock_geocoder = Mock()
        mock_geocoder.geocode.side_effect = GeocoderTimedOut("Timeout")
        mock_nominatim_class.return_value = mock_geocoder

        service = GeocodingService()
        result = service.geocode_location("Some Location")

        assert result is None

    @patch("app.services.geocoding.Nominatim")
    def test_geocode_location_service_error(self, mock_nominatim_class):
        # Mock service error
        mock_geocoder = Mock()
        mock_geocoder.geocode.side_effect = GeocoderServiceError("Service error")
        mock_nominatim_class.return_value = mock_geocoder

        service = GeocodingService()
        result = service.geocode_location("Some Location")

        assert result is None

    @patch("app.services.geocoding.Nominatim")
    @patch("app.services.geocoding.time.sleep")
    def test_geocode_location_rate_limiting(self, mock_sleep, mock_nominatim_class):
        # Test that rate limiting delay is applied
        mock_geocoder = Mock()
        mock_location = Mock()
        mock_location.latitude = 51.5074
        mock_location.longitude = -0.1278
        mock_location.raw = {
            "boundingbox": ["51.3918", "51.6723", "-0.3514", "0.1480"],
            "class": "place",
            "type": "city",
            "address": {"city": "London", "country": "United Kingdom"},
            "extratags": {"admin_level": "8"},
        }
        mock_geocoder.geocode.return_value = mock_location
        mock_nominatim_class.return_value = mock_geocoder

        service = GeocodingService()
        result = service.geocode_location("London")

        assert result == (51.5074, -0.1278)
        mock_sleep.assert_called_once_with(0.1)
