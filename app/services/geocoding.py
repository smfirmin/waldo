from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Tuple, Optional
import time


class GeocodingService:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="waldo")

    def geocode_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert location name to latitude, longitude coordinates.
        Returns: (latitude, longitude) or None if not found
        """
        try:
            # Add small delay to be respectful to the service
            time.sleep(0.1)

            location = self.geocoder.geocode(location_name, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error for '{location_name}': {e}")
            return None
        except Exception as e:
            print(f"Unexpected error geocoding '{location_name}': {e}")
            return None
