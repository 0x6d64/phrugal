from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import exifread
from PIL import Image, ImageDraw, ImageFont
from exifread.classes import IfdTag

from . import PixelTuple
from .border_decoration import BorderDecoration

MM_PER_INCH = 25.4


def _calc_common_values() -> list[int]:
    base_values = {
        2500,
        2000,
        1600,
        1250,
        1000,
        800,
        640,
        500,
        400,
        320,
        250,
        200,
        160,
        125,
        100,
        80,
        60,
        50,
        40,
        30,
        25,
        20,
        15,
        13,
        10,
        8,
        6,
        5,
        4,
        2,
    }
    retval = sorted([float(x) for x in base_values])
    return retval


@dataclass
class PhrugalImage:
    def __init__(self, file_name: Path | str) -> None:
        self.file_name = file_name
        self._image = Image.open(self.file_name, mode="r")
        pass

    @property
    def image_dims(self) -> PixelTuple:
        return self._image.size

    def get_decorated_image(self, decoration: BorderDecoration) -> Image:
        new_img = Image.new(
            "RGB",
            decoration.get_size_with_border(self.image_dims),
            color=decoration.background_color,
        )
        new_img.paste(self._image, decoration.get_border_size(self.image_dims))
        self._draw_text(new_img, decoration)

        return new_img

    def _draw_text(self, img: Image, decoration: BorderDecoration) -> None:
        draw = ImageDraw.Draw(img)
        font = self._get_font(decoration)
        border_x, border_y = decoration.get_border_size(self.image_dims)

        text = self._get_text()
        text_offset_pixel = int(
            (border_x - decoration.get_font_size(self.image_dims)) * 0.5
        )
        text_origin = (
            text_offset_pixel + border_x,
            text_offset_pixel + self.image_dims[1] + border_y,
        )
        draw.text(text_origin, text, fill=decoration.text_color, font=font)

    def _get_text(self) -> str:
        # 50mm | f/2.8 | 1/250s | ISO 400
        exif = PhrugalExifData(self.file_name)

        # f_len = exif.get_ifd(ExifTags.Base.FocalLength)
        # aperture = exif.get_ifd(ExifTags.Base.ApertureValue)
        # exp = exif.get_ifd(ExifTags.Base.ExposureTime)
        # iso = exif.get_ifd(ExifTags.Base.ISOSpeed)
        candidates = [
            exif.get_focal_len(),
            exif.get_aperture(),
            exif.get_shutter_speed(),
            exif.get_iso(),
        ]
        t = " | ".join([x for x in candidates if x])
        return t

    def _get_font(self, decoration: BorderDecoration) -> ImageFont.FreeTypeFont:
        font_size = int(decoration.get_font_size(self.image_dims))
        if decoration.font is None:
            font = ImageFont.truetype("arial.ttf", size=font_size)
        else:
            font = ImageFont.truetype(decoration.font, size=font_size)
        return font

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._image.close()
        return False


class PhrugalExifData:
    COMMON_DIVIDEND_VALUES = _calc_common_values()
    THRESHOLD_COMMON_DISPLAY = 0.08
    THRESHOLD_FRACTION_DISPLAY = 0.55

    def __init__(self, image_path: Path | str) -> None:
        self._image_path = image_path
        with open(image_path, "rb") as fp:
            self.exif_data = exifread.process_file(fp)

    def __repr__(self):
        return Path(self._image_path).name

    def get_focal_len(self) -> str | None:
        raw = self.exif_data.get("EXIF FocalLength", None)  # type: Optional[IfdTag]
        if raw is None:
            return None
        else:
            value = float(raw.values[0])
            return f"{value:.1f}mm"

    def get_aperture(self) -> str | None:
        raw = self.exif_data.get("EXIF ApertureValue", None)
        if raw is None:
            return None
        else:
            value = float(raw.values[0])
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
                exposure_dividend = self.round_shutter_to_common_value(
                    float(exposure_dividend)
                )
                div_rounded = int(exposure_dividend)
                return f"1/{div_rounded}s"
            else:
                return f"{exposure_time:.1f}s"

    def round_shutter_to_common_value(self, dividend: float) -> float:
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
