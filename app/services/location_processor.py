import concurrent.futures
import logging
from typing import List, Tuple
from app.models.data_models import ArticleResponse, LocationData, ExtractedLocation
from app.services.geocoding import GeocodingService, GeographicData
from app.services.summarizer import EventSummarizer

logger = logging.getLogger(__name__)


class LocationProcessor:
    def __init__(self, geocoding_service: GeocodingService):
        self.geocoding_service = geocoding_service

    def filter_by_spatial_hierarchy(
        self, geo_data_list: List[GeographicData]
    ) -> List[int]:
        """
        Filter locations using spatial containment to keep only the most specific locations.
        If location A contains location B, keep B (the more specific one).

        Returns indices of locations to keep.
        """
        if len(geo_data_list) <= 1:
            return list(range(len(geo_data_list)))

        keep_indices = []

        for i, location in enumerate(geo_data_list):
            should_keep = True

            # Check if any other location is contained within this location
            # If so, this location is broader and should be filtered out
            for j, other_location in enumerate(geo_data_list):
                if i == j:
                    continue

                # If other location is contained within current location,
                # then current location is broader and should be filtered out
                if self.geocoding_service.is_contained_within(other_location, location):
                    logger.info(
                        f"Filtering out {location.name} (contains more specific {other_location.name})"
                    )
                    should_keep = False
                    break

            if should_keep:
                keep_indices.append(i)

        return keep_indices

    def process_locations_pipeline(
        self,
        extracted_locations: List[ExtractedLocation],
        article_text: str,
        summarizer: EventSummarizer,
        response: ArticleResponse,
        request_id: str,
    ) -> Tuple[List[LocationData], List[GeographicData]]:
        """
        Process extracted locations through geocoding and summarization pipeline.

        Returns:
            Tuple of (location_data_list, geo_data_list)
        """

        def process_location(extracted_loc) -> Tuple[LocationData, GeographicData]:
            # Geocode location with boundary data
            geo_data = self.geocoding_service.geocode_with_boundaries(
                extracted_loc.standardized_name
            )
            if not geo_data:
                logger.warning(
                    f"Request {request_id}: Failed to geocode {extracted_loc.standardized_name}"
                )
                return None, None

            # Generate summary for this location
            summary = summarizer.summarize_events_at_location(
                article_text, extracted_loc.standardized_name
            )

            # Calculate confidence score
            confidence = 0.8  # Base confidence
            if extracted_loc.confidence == "high":
                confidence = 0.9
            elif extracted_loc.confidence == "low":
                confidence = 0.6

            location_data = LocationData(
                name=extracted_loc.standardized_name,
                latitude=geo_data.latitude,
                longitude=geo_data.longitude,
                events_summary=summary,
                confidence=confidence,
                resolution_method="direct",
                original_text=extracted_loc.original_text,
            )

            return location_data, geo_data

        # Use ThreadPoolExecutor for parallel processing
        locations = []
        geo_data_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_location = {
                executor.submit(process_location, loc): loc.standardized_name
                for loc in extracted_locations
            }

            for future in concurrent.futures.as_completed(future_to_location):
                location_data, geo_data = future.result()
                if (
                    location_data and geo_data
                ):  # Only add successfully geocoded locations
                    locations.append(location_data)
                    geo_data_list.append(geo_data)
                    logger.info(
                        f"Request {request_id}: Successfully processed {location_data.name}"
                    )
                else:
                    # Add warning for failed locations
                    failed_name = future_to_location[future]
                    response.add_warning(
                        "GEOCODING_FAILED",
                        f"Could not find coordinates for '{failed_name}'",
                    )

        return locations, geo_data_list

    def apply_spatial_filtering(
        self,
        locations: List[LocationData],
        geo_data_list: List[GeographicData],
        response: ArticleResponse,
        request_id: str,
    ) -> List[LocationData]:
        """
        Apply spatial hierarchical filtering to remove broader locations.

        Returns:
            Filtered list of locations
        """
        if len(geo_data_list) <= 1:
            return locations

        filtered_indices = self.filter_by_spatial_hierarchy(geo_data_list)
        if len(filtered_indices) < len(locations):
            removed_count = len(locations) - len(filtered_indices)
            response.add_warning(
                "SPATIAL_HIERARCHY_FILTERED",
                f"Filtered out {removed_count} broader location(s) contained within more specific ones",
            )
            logger.info(
                f"Request {request_id}: Filtered {removed_count} locations due to spatial hierarchy"
            )

        # Keep only the filtered locations
        return [locations[i] for i in filtered_indices]
