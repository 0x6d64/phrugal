from pathlib import Path
from typing import Optional

import exifread
from exifread.classes import IfdTag


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

    def _round_shutter_to_common_value(self, dividend: float) -> float:
        closest_common_value = min(
            self.COMMON_DIVIDEND_VALUES, key=lambda a: abs(a - dividend)
        )
        deviation_from_closest = abs(dividend - closest_common_value) / dividend

        if deviation_from_closest > self.THRESHOLD_COMMON_DISPLAY:
            return dividend
        else:
            return closest_common_value

    def get_iso(self) -> str | None:
        raw = self.exif_data.get("EXIF ISOSpeedRatings", None)
        if raw is None:
            return None
        else:
            return f"ISO {raw}"
