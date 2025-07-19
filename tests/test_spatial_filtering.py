from unittest.mock import Mock
from app.services.geocoding import GeographicData, GeocodingService
from app.services.location_processor import LocationProcessor


class TestSpatialFiltering:
    def setup_method(self):
        """Setup for each test method"""
        self.mock_geocoding_service = Mock(spec=GeocodingService)
        self.location_processor = LocationProcessor(self.mock_geocoding_service)

    def test_filter_usa_and_washington_dc(self):
        """Test filtering when both USA and Washington DC are present"""
        usa_data = GeographicData(
            name="United States",
            latitude=39.8283,
            longitude=-98.5795,
            bounding_box=(18.9110642, 71.3578877, -179.2311342, 179.8597345),
            admin_level=2,
            place_type="country",
            containing_areas={},
        )

        dc_data = GeographicData(
            name="Washington DC",
            latitude=38.9072,
            longitude=-77.0369,
            bounding_box=(38.791645, 38.9955847, -77.1198998, -76.9093017),
            admin_level=4,
            place_type="city",
            containing_areas={"country": "United States"},
        )

        # Mock the containment check - DC is contained within USA
        def mock_is_contained_within(location1, location2):
            if location1.name == "Washington DC" and location2.name == "United States":
                return True
            return False

        self.mock_geocoding_service.is_contained_within.side_effect = (
            mock_is_contained_within
        )

        # Test filtering
        geo_data_list = [usa_data, dc_data]
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should keep only Washington DC (index 1), filter out USA (index 0)
        assert result_indices == [1]

    def test_filter_california_and_los_angeles(self):
        """Test filtering when both California and Los Angeles are present"""
        ca_data = GeographicData(
            name="California",
            latitude=36.7783,
            longitude=-119.4179,
            bounding_box=(32.528832, 42.009518, -124.482003, -114.131211),
            admin_level=4,
            place_type="state",
            containing_areas={},
        )

        la_data = GeographicData(
            name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
            bounding_box=(33.7037, 34.3373, -118.6682, -118.1553),
            admin_level=8,
            place_type="city",
            containing_areas={"state": "California"},
        )

        # Mock the containment check - LA is contained within California
        def mock_is_contained_within(location1, location2):
            if location1.name == "Los Angeles" and location2.name == "California":
                return True
            return False

        self.mock_geocoding_service.is_contained_within.side_effect = (
            mock_is_contained_within
        )

        # Test filtering
        geo_data_list = [ca_data, la_data]
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should keep only Los Angeles (index 1), filter out California (index 0)
        assert result_indices == [1]

    def test_filter_unrelated_locations(self):
        """Test filtering when locations are not spatially related"""
        nyc_data = GeographicData(
            name="New York City",
            latitude=40.7128,
            longitude=-74.0060,
            bounding_box=(40.4774, 40.9176, -74.2591, -73.7004),
            admin_level=8,
            place_type="city",
            containing_areas={},
        )

        london_data = GeographicData(
            name="London",
            latitude=51.5074,
            longitude=-0.1278,
            bounding_box=(51.2867, 51.6918, -0.5103, 0.3340),
            admin_level=8,
            place_type="city",
            containing_areas={},
        )

        # Mock the containment check - no containment
        self.mock_geocoding_service.is_contained_within.return_value = False

        # Test filtering
        geo_data_list = [nyc_data, london_data]
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should keep both locations (indices 0 and 1)
        assert result_indices == [0, 1]

    def test_filter_multiple_cities_same_state(self):
        """Test filtering multiple cities in the same state"""
        sf_data = GeographicData(
            name="San Francisco",
            latitude=37.7749,
            longitude=-122.4194,
            bounding_box=(37.7037, 37.8324, -122.5150, -122.3570),
            admin_level=8,
            place_type="city",
            containing_areas={},
        )

        la_data = GeographicData(
            name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
            bounding_box=(33.7037, 34.3373, -118.6682, -118.1553),
            admin_level=8,
            place_type="city",
            containing_areas={},
        )

        # Mock the containment check - no containment between cities
        self.mock_geocoding_service.is_contained_within.return_value = False

        # Test filtering
        geo_data_list = [sf_data, la_data]
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should keep both cities (indices 0 and 1)
        assert result_indices == [0, 1]

    def test_filter_single_location(self):
        """Test filtering with single location"""
        paris_data = GeographicData(
            name="Paris",
            latitude=48.8566,
            longitude=2.3522,
            bounding_box=(48.8155755, 48.9021449, 2.2249775, 2.4699208),
            admin_level=8,
            place_type="city",
            containing_areas={},
        )

        # Test filtering
        geo_data_list = [paris_data]
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should keep the single location (index 0)
        assert result_indices == [0]

    def test_filter_empty_list(self):
        """Test filtering with empty list"""
        # Test filtering
        geo_data_list = []
        result_indices = self.location_processor.filter_by_spatial_hierarchy(
            geo_data_list
        )

        # Should return empty list
        assert result_indices == []
