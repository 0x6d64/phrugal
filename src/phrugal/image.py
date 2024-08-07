from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .types import Dimensions
from .border_decoration import BorderDecoration
from .exif import PhrugalExifData



MM_PER_INCH = 25.4


@dataclass
class PhrugalImage:
    def __init__(self, file_name: Path | str) -> None:
        self.file_name = Path(file_name)
        self._image = Image.open(self.file_name, mode="r")

    @property
    def image_dims(self) -> Dimensions:
        return self._image.size

    @property
    def aspect_ratio(self) -> float:
        """y_dim / x_dim"""
        x_dim, y_dim = self.image_dims
        return float(x_dim) / float(y_dim)

    @property
    def aspect_ratio_normalized(self) -> float:
        """Same as aspect ratio, but assume that we rotate portrait orientation to landscape always"""
        return self.aspect_ratio if self.aspect_ratio > 1 else 1 / self.aspect_ratio

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

    def close_image(self):
        self._image.close()

    def __repr__(self):
        return f"{self.file_name.name}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._image.close()
        return False

    def __del__(self):
        self._image.close()
