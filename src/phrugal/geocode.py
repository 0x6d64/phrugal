import logging
from functools import cache

import phrugal
from geopy import Point
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

USER_AGENT = f"phrugal/{phrugal.__version__} (+https://github.com/0x6d64/phrugal)"


def get_geocoder() -> Nominatim:
    return Nominatim(user_agent=USER_AGENT)


class Geocoder:
    GEOCODER = None
    _CALLS_MADE = 0
    MIN_DELAY_SECONDS = 1.1
    ERROR_WAIT_SECONDS = 7
    MAX_RETRIES = 5
    DEFAULT_ZOOM = 12
    DEFAULT_LOCATION_NAME_PARTS = ["road", "city", "county", "state", "country"]
    ALLOWED_LOCATION_NAME_PARTS = [
        "historic",
        "house_number",
        "road",
        "neighbourhood",
        "suburb",
        "city",
        "state",
        "county",
        "ISO3166-2-lvl4",
        "postcode",
        "country",
        "country_code",
    ]

    def __init__(self):
        if self.GEOCODER is None:
            self.GEOCODER = get_geocoder()
            self._reverse_rate_limited = RateLimiter(
                self.GEOCODER.reverse,
                min_delay_seconds=self.MIN_DELAY_SECONDS,
                max_retries=self.MAX_RETRIES,
                error_wait_seconds=self.ERROR_WAIT_SECONDS,
            )

    def get_location_name(
        self,
        lat: float,
        lon: float,
        zoom: int = DEFAULT_ZOOM,
        name_parts: list[str] = DEFAULT_LOCATION_NAME_PARTS,  # noqa
    ) -> str:
        """Returns a name for given coordinates

        Note: The selection of the values that are returned and omitted are highly subjective.
        This is since in e.g. Germany the neighbourhood value does not match the real world name
        that people use for the location.

        :param lat: latitude
        :param lon: longitude
        :param zoom: zoom level, see https://nominatim.org/release-docs/develop/api/Reverse/#result-restriction
        :return: formatted location name
        """
        loc = Point(lat, lon)
        return self.get_location_name_from_point(loc, zoom=zoom, name_parts=name_parts)

    def get_location_name_from_point(
        self,
        loc: Point,
        zoom: int = DEFAULT_ZOOM,
        name_parts: list[str] = DEFAULT_LOCATION_NAME_PARTS,  # noqa
    ) -> str:
        for p in name_parts:
            if p not in self.ALLOWED_LOCATION_NAME_PARTS:
                raise RuntimeError(f"configured location name part {p} is not known!")
        # call API endpoint, pass lat and lon since Point is not hashable
        answer = self._call_reverse_api(lat=loc.latitude, lon=loc.longitude, zoom=zoom)
        self._CALLS_MADE += 1
        address_dict = answer.raw["address"]
        name_parts_from_server = [address_dict.get(x) for x in name_parts]
        name_formatted = ", ".join(x for x in name_parts_from_server if x)

        return name_formatted

    @cache
    def _call_reverse_api(self, lat, lon, zoom: int):
        """Call the reverse api end point.

        We isolate this into its own method to make it cacheable. We pass lat and lon instead of Point
        since Point instances are not hashable.
        """
        loc = Point(lat, lon)
        answer = self._reverse_rate_limited(loc, exactly_one=True, zoom=zoom)
        return answer
