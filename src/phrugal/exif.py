from pathlib import Path
from typing import Optional, Tuple
from typing import TYPE_CHECKING

import exifread
from exifread.classes import IfdTag

from exifread.utils import Ratio


def get_common_values() -> list[float]:
    """Provide a sequence of commonly used values.

    Since there is no easy rule for these values, they are hard coded.
    """
    # fmt: off
    base_values = {
        2500, 2000, 1600, 1250, 1000,
        800, 640, 500, 400, 320, 250, 200, 160, 125, 100,
        80, 60, 50, 40, 30, 25, 20, 15, 13, 10,
        8, 6, 5, 4, 2,
    }
    # fmt: on
    retval = sorted([float(x) for x in base_values])
    return retval


class PhrugalExifData:
    COMMON_DIVIDEND_VALUES = get_common_values()
    THRESHOLD_COMMON_DISPLAY = (
        0.08  # how many deviation is allowed before "snapping" onto common value
    )
    THRESHOLD_FRACTION_DISPLAY = (
        0.55  # smaller values are displayed as fractions of seconds
    )
    THRESHOLD_APERTURE_INF = 1e8  # bigger values are considered infinite/tiny
    INF_APERTURE_REPRESENTATION = "inf"  # represent tiny apertures like this

    def __init__(self, image_path: Path | str) -> None:
        self.image_path = image_path
        with open(image_path, "rb") as fp:
            self.exif_data = exifread.process_file(fp)

    def __repr__(self):
        return Path(self.image_path).name

    def get_focal_len(self) -> str | None:
        raw = self.exif_data.get("EXIF FocalLength", None)  # type: Optional[IfdTag]
        if raw is None:
            return None
        else:
            value = float(raw.values[0])
            return f"{value:1.0f}mm"

    def get_aperture(self) -> str | None:
        raw = self.exif_data.get("EXIF ApertureValue", None)
        if raw is None:
            return None
        else:
            value = float(raw.values[0])
            if value > self.THRESHOLD_APERTURE_INF:
                return str(self.INF_APERTURE_REPRESENTATION)
            return f"f/{value:.1f}"

    def get_shutter_speed(self) -> str | None:
        raw = self.exif_data.get("EXIF ShutterSpeedValue", None)
        if raw is None:
            return None
        else:
            apex = raw.values[0]
            exposure_time = 2 ** (-apex)
            exposure_dividend = 2**apex
            if exposure_time < self.THRESHOLD_FRACTION_DISPLAY:
                exposure_dividend = self._round_shutter_to_common_value(
                    float(exposure_dividend)
                )
                div_rounded = int(exposure_dividend)
                return f"1/{div_rounded}s"
            else:
                return f"{exposure_time:.1f}s"

    def get_iso(self) -> str | None:
        raw = self.exif_data.get("EXIF ISOSpeedRatings", None)
        if raw is None:
            return None
        else:
            return f"ISO {raw}"

    def get_gps(
        self, include_altitude: bool = True, use_dms: bool = True
    ) -> str | None:
        lat = self.exif_data.get("GPS GPSLatitude", None)
        lat_ref = self.exif_data.get("GPS GPSLatitudeRef", None)
        long = self.exif_data.get("GPS GPSLongitude", None)
        long_ref = self.exif_data.get("GPS GPSLongitudeRef", None)
        alt = self.exif_data.get("GPS GPSAltitude", None)

        have_gps_fix = all([lat, lat_ref, long, long_ref])
        have_altitude = alt is not None

        if have_gps_fix:
            gps_formatted = self._represent_gps_data(
                lat, lat_ref, long, long_ref, format="dms" if use_dms else "dds"
            )

            if have_altitude and include_altitude:
                altidue_value = float(alt.values[0])
                gps_formatted += f", {altidue_value:1.0f}m"
        else:
            return None

        return gps_formatted

    @classmethod
    def _represent_gps_data(
        cls, lat: list, lat_ref, lon: list, lon_ref, format: str = "dms"
    ) -> str:
        lat_deg, lat_min, lat_sec = cls._ratios_to_coordinates(lat.values)
        lon_deg, lon_min, lon_sec = cls._ratios_to_coordinates(lon.values)

        # fmt: off
        if format == "dms":  # degree, minute, second
            lat_formatted = f"{lat_deg:1.0f}°{lat_min:1.0f}'{lat_sec:1.1f}\"{str(lat_ref)}"
            lon_formatted = f"{lon_deg:1.0f}°{lon_min:1.0f}'{lon_sec:1.1f}\"{str(lon_ref)}"
        elif format == "dds":  # degree, decimal minute
            lat_min += lat_sec / 60
            lon_min += lon_sec / 60
            lat_formatted = f"{lat_deg:1.0f}°{lat_min:1.3f}'{str(lat_ref)}"
            lon_formatted = f"{lon_deg:1.0f}°{lon_min:1.3f}'{str(lon_ref)}"
        else:
            raise ValueError(f"Unsupported format: {format}")
        # fmt: on
        return f"{lat_formatted}, {lon_formatted}"

    @staticmethod
    def _ratios_to_coordinates(data: list[Ratio]) -> Tuple[float, float, float]:
        degree = float(data[0])
        minute = float(data[1])
        second = float(data[2])

        remainder_degree = degree - int(degree)
        degree -= remainder_degree
        minute += remainder_degree * 60

        remainder_minute = minute - int(minute)
        minute -= remainder_minute
        second += remainder_minute * 60

        return degree, minute, second

    def _round_shutter_to_common_value(self, dividend: float) -> float:
        closest_common_value = min(
            self.COMMON_DIVIDEND_VALUES, key=lambda a: abs(a - dividend)
        )
        deviation_from_closest = abs(dividend - closest_common_value) / dividend

        if deviation_from_closest > self.THRESHOLD_COMMON_DISPLAY:
            return dividend
        else:
            return closest_common_value
