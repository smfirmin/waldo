from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Tuple, Optional, Dict
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeographicData:
    """Geographic information for a location"""

    name: str
    latitude: float
    longitude: float
    bounding_box: Optional[
        Tuple[float, float, float, float]
    ] = None  # (south, north, west, east)
    admin_level: Optional[
        int
    ] = None  # Administrative level (2=country, 4=state, 8=city, etc.)
    place_type: Optional[str] = None  # country, state, city, etc.
    containing_areas: Optional[Dict[str, str]] = None  # {admin_level: area_name}


class GeocodingService:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="waldo")

    def geocode_with_boundaries(self, location_name: str) -> Optional[GeographicData]:
        """
        Convert location name to detailed geographic data including boundaries.
        Returns: GeographicData object or None if not found
        """
        try:
            # Add small delay to be respectful to the service
            time.sleep(0.1)

            # Request detailed data from Nominatim
            location = self.geocoder.geocode(
                location_name,
                timeout=10,
                exactly_one=True,
                addressdetails=True,
                extratags=True,
            )

            if not location:
                return None

            # Extract bounding box
            bounding_box = None
            if hasattr(location, "raw") and "boundingbox" in location.raw:
                bbox = location.raw["boundingbox"]
                # Nominatim returns [south, north, west, east]
                bounding_box = (
                    float(bbox[0]),
                    float(bbox[1]),
                    float(bbox[2]),
                    float(bbox[3]),
                )

            # Extract administrative level and place type
            admin_level = None
            place_type = None
            containing_areas = {}

            if hasattr(location, "raw") and location.raw:
                raw_data = location.raw

                # Get place type from class/type
                if "class" in raw_data:
                    place_type = raw_data.get("type", raw_data["class"])

                # Extract admin level from extratags
                if (raw_data.get("extratags") and 
                    "admin_level" in raw_data["extratags"]):
                    try:
                        admin_level = int(raw_data["extratags"]["admin_level"])
                    except (ValueError, TypeError):
                        pass

                # Extract containing administrative areas from address
                if raw_data.get("address"):
                    address = raw_data["address"]
                    containing_areas = {
                        "country": address.get("country"),
                        "state": address.get("state"),
                        "county": address.get("county"),
                        "city": address.get("city"),
                        "town": address.get("town"),
                        "village": address.get("village"),
                    }
                    # Remove None values
                    containing_areas = {k: v for k, v in containing_areas.items() if v}

            return GeographicData(
                name=location_name,
                latitude=location.latitude,
                longitude=location.longitude,
                bounding_box=bounding_box,
                admin_level=admin_level,
                place_type=place_type,
                containing_areas=containing_areas,
            )

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding error for '{location_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{location_name}': {e}")
            return None

    def is_contained_within(
        self, location1: GeographicData, location2: GeographicData
    ) -> bool:
        """
        Check if location1 is geographically contained within location2.
        Returns True if location1 is inside location2's boundaries.
        """
        # If either location lacks bounding box, fall back to administrative hierarchy
        if not location1.bounding_box or not location2.bounding_box:
            return self._check_administrative_containment(location1, location2)

        # Check if location1's point is within location2's bounding box
        lat1, lon1 = location1.latitude, location1.longitude
        south2, north2, west2, east2 = location2.bounding_box

        # Simple point-in-bbox check
        if south2 <= lat1 <= north2 and west2 <= lon1 <= east2:
            return True

        # If location1 has a bounding box, check if it's entirely within location2
        if location1.bounding_box:
            south1, north1, west1, east1 = location1.bounding_box
            return (
                south2 <= south1
                and north1 <= north2
                and west2 <= west1
                and east1 <= east2
            )

        return False

    def _check_administrative_containment(
        self, location1: GeographicData, location2: GeographicData
    ) -> bool:
        """
        Check containment using administrative hierarchy when bounding boxes aren't available.
        """
        if not location1.containing_areas or not location2.containing_areas:
            return False

        # Check if location2's name appears in location1's containing areas
        location2_name_lower = location2.name.lower()
        for area_name in location1.containing_areas.values():
            if area_name and area_name.lower() == location2_name_lower:
                return True

        return False
