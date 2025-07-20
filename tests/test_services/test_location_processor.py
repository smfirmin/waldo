from unittest.mock import Mock, patch
from app.services.location_processor import LocationProcessor
from app.models.data_models import ArticleResponse, LocationData, ExtractedLocation
from app.services.geocoding import GeographicData
from app.services.summarizer import EventSummarizer


class TestLocationProcessor:
    def setup_method(self):
        self.mock_geocoding_service = Mock()
        self.processor = LocationProcessor(self.mock_geocoding_service)

    def test_filter_by_spatial_hierarchy_empty_list(self):
        result = self.processor.filter_by_spatial_hierarchy([])
        assert result == []

    def test_filter_by_spatial_hierarchy_single_location(self):
        geo_data = Mock(spec=GeographicData)
        result = self.processor.filter_by_spatial_hierarchy([geo_data])
        assert result == [0]

    def test_filter_by_spatial_hierarchy_no_containment(self):
        geo_data1 = Mock(spec=GeographicData, name="Location1")
        geo_data2 = Mock(spec=GeographicData, name="Location2")

        self.mock_geocoding_service.is_contained_within.return_value = False

        result = self.processor.filter_by_spatial_hierarchy([geo_data1, geo_data2])
        assert result == [0, 1]

    def test_filter_by_spatial_hierarchy_with_containment(self):
        broader_location = Mock(spec=GeographicData)
        broader_location.name = "State"
        specific_location = Mock(spec=GeographicData)
        specific_location.name = "City"

        # City is contained within State
        def mock_is_contained_within(location1, location2):
            if location1 == specific_location and location2 == broader_location:
                return True
            return False

        self.mock_geocoding_service.is_contained_within.side_effect = (
            mock_is_contained_within
        )

        result = self.processor.filter_by_spatial_hierarchy(
            [broader_location, specific_location]
        )
        assert result == [1]  # Keep only the specific location (index 1)

    def test_filter_by_spatial_hierarchy_complex_scenario(self):
        country = Mock(spec=GeographicData)
        country.name = "Country"
        state = Mock(spec=GeographicData)
        state.name = "State"
        city = Mock(spec=GeographicData)
        city.name = "City"

        def mock_is_contained_within(location1, location2):
            if location1 == city and location2 == state:
                return True
            if location1 == state and location2 == country:
                return True
            if location1 == city and location2 == country:
                return True
            return False

        self.mock_geocoding_service.is_contained_within.side_effect = (
            mock_is_contained_within
        )

        result = self.processor.filter_by_spatial_hierarchy([country, state, city])
        assert result == [2]  # Keep only the most specific location (city)

    def test_process_locations_pipeline_success(self):
        extracted_location = ExtractedLocation(
            original_text="New York",
            standardized_name="New York City",
            context="Event in New York",
            confidence="high",
            location_type="city",
            disambiguation_hints=[],
        )

        geo_data = GeographicData(
            name="New York City",
            latitude=40.7128,
            longitude=-74.0060,
            bounding_box=(-74.2591, 40.4774, -73.7004, 40.9176),
            admin_level=8,
            place_type="city",
        )

        article_text = "News about events in New York City"
        mock_summarizer = Mock(spec=EventSummarizer)
        mock_summarizer.summarize_events_at_location.return_value = "Summary of events"

        response = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )
        request_id = "test-123"

        # Mock the geocoding service
        self.mock_geocoding_service.geocode_with_boundaries.return_value = geo_data

        # Test the pipeline by calling it directly
        locations, geo_data_list = self.processor.process_locations_pipeline(
            [extracted_location], article_text, mock_summarizer, response, request_id
        )

        # Verify results
        assert len(locations) == 1
        assert len(geo_data_list) == 1
        assert locations[0].name == "New York City"
        assert locations[0].confidence == 0.9
        assert locations[0].events_summary == "Summary of events"

    def test_process_locations_pipeline_geocoding_failure(self):
        extracted_location = ExtractedLocation(
            original_text="Unknown Place",
            standardized_name="Unknown Place",
            context="Event at unknown place",
            confidence="medium",
            location_type="city",
            disambiguation_hints=[],
        )

        article_text = "News about events"
        mock_summarizer = Mock(spec=EventSummarizer)
        response = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )
        request_id = "test-123"

        # Mock geocoding failure
        self.mock_geocoding_service.geocode_with_boundaries.return_value = None

        locations, geo_data_list = self.processor.process_locations_pipeline(
            [extracted_location], article_text, mock_summarizer, response, request_id
        )

        assert len(locations) == 0
        assert len(geo_data_list) == 0
        assert len(response.warnings) == 1
        assert response.warnings[0].code == "GEOCODING_FAILED"

    def test_apply_spatial_filtering_single_location(self):
        location = LocationData(
            name="Test Location",
            latitude=40.0,
            longitude=-74.0,
            events_summary="Test summary",
            confidence=0.8,
            resolution_method="direct",
            original_text="Test",
        )

        geo_data = Mock(spec=GeographicData)
        response = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )
        request_id = "test-123"

        result = self.processor.apply_spatial_filtering(
            [location], [geo_data], response, request_id
        )

        assert len(result) == 1
        assert result[0] == location

    def test_apply_spatial_filtering_with_hierarchy(self):
        broader_location = LocationData(
            name="State",
            latitude=40.0,
            longitude=-74.0,
            events_summary="State summary",
            confidence=0.8,
            resolution_method="direct",
            original_text="State",
        )

        specific_location = LocationData(
            name="City",
            latitude=40.1,
            longitude=-74.1,
            events_summary="City summary",
            confidence=0.9,
            resolution_method="direct",
            original_text="City",
        )

        broader_geo = Mock(spec=GeographicData)
        broader_geo.name = "State"
        specific_geo = Mock(spec=GeographicData)
        specific_geo.name = "City"

        response = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )
        request_id = "test-123"

        # Mock filter_by_spatial_hierarchy to return only the specific location
        with patch.object(
            self.processor, "filter_by_spatial_hierarchy", return_value=[1]
        ):
            result = self.processor.apply_spatial_filtering(
                [broader_location, specific_location],
                [broader_geo, specific_geo],
                response,
                request_id,
            )

        assert len(result) == 1
        assert result[0] == specific_location
        assert len(response.warnings) == 1
        assert response.warnings[0].code == "SPATIAL_HIERARCHY_FILTERED"

    def test_confidence_score_calculation(self):
        # Test high confidence
        high_conf_location = ExtractedLocation(
            original_text="Test",
            standardized_name="Test Location",
            context="Context",
            confidence="high",
            location_type="city",
            disambiguation_hints=[],
        )

        geo_data = GeographicData(
            name="Test Location",
            latitude=40.0,
            longitude=-74.0,
            bounding_box=(-75.0, 39.0, -73.0, 41.0),
            admin_level=8,
            place_type="city",
        )

        self.mock_geocoding_service.geocode_with_boundaries.return_value = geo_data
        mock_summarizer = Mock(spec=EventSummarizer)
        mock_summarizer.summarize_events_at_location.return_value = "Test summary"

        response = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )
        request_id = "test"

        locations, _ = self.processor.process_locations_pipeline(
            [high_conf_location], "article text", mock_summarizer, response, request_id
        )

        assert locations[0].confidence == 0.9

        # Test low confidence
        low_conf_location = ExtractedLocation(
            original_text="Test",
            standardized_name="Test Location",
            context="Context",
            confidence="low",
            location_type="city",
            disambiguation_hints=[],
        )

        response2 = ArticleResponse(
            article_text="Sample article text", locations=[], processing_time=0.0
        )

        locations2, _ = self.processor.process_locations_pipeline(
            [low_conf_location], "article text", mock_summarizer, response2, request_id
        )

        assert locations2[0].confidence == 0.6
