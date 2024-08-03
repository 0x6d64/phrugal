from functools import cache

from geopy import Point
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

USER_AGENT = "phrugal/0.1"


def get_geocoder() -> Nominatim:
    return Nominatim(user_agent=USER_AGENT)


class Gecoder:
    GEOCODER = None
    _CALLS_MADE = 0
    MIN_DELAY_SECONDS = 1.05

    def __init__(self):
        if self.GEOCODER is None:
            self.GEOCODER = get_geocoder()
            self._reverse_rate_limited = RateLimiter(
                self.GEOCODER.reverse, min_delay_seconds=self.MIN_DELAY_SECONDS
            )

    @cache
    def get_location_name(
        self, lat: float, lon: float, alt: float = 0.0, zoom: int = 12
    ) -> str:
        """Returns a name for given coordinates

        Note: The selection of the values that are returned and omitted are highly subjective.
        This is since in e.g. Germany the neighbourhood value does not match the real world name
        that people use for the location.

        :param lat: latitude
        :param lon: longitude
        :param alt: altitude
        :param zoom: zoom level, see https://nominatim.org/release-docs/develop/api/Reverse/#result-restriction
        :return: formatted location name
        """
        loc = Point(lat, lon, alt)
        answer = self._reverse_rate_limited(loc, exactly_one=True, zoom=zoom)
        self._CALLS_MADE += 1
        address_dict = answer.raw["address"]
        name_parts = [
            address_dict.get("road"),
            address_dict.get("city"),
            address_dict.get("county"),
            address_dict.get("state"),
            address_dict.get("country"),
        ]
        name_formatted = ", ".join(x for x in name_parts if x)
        return name_formatted
