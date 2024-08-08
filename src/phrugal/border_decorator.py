from fractions import Fraction
from typing import Optional

import PIL.Image as PilImage
from PIL.ImageColor import getrgb
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

from .image import PhrugalImage
from .types import ColorTuple, Dimensions


def add_dimensions(a: Dimensions, b: Dimensions) -> Dimensions:
    assert len(a) == len(b) == 2
    a_x, a_y = a
    b_x, b_y = b
    return int(a_x + b_x), int(a_y + b_y)


def scale_dimensions(d: Dimensions, scale: float) -> Dimensions:
    x, y = d
    new_dim = int(x * scale), int(y * scale)
    return new_dim


class BorderDecorator:
    """Represents geometry of an image border and the text written on it"""

    TEXT_RATIO = 0.7  # how many percent of the border shall be covered by text
    FONT_CACHE = dict()
    DEFAULT_FONT = "arial.ttf"
    BORDER_MULTIPLIER = 1.0
    NOMINAL_LEN_LARGER_SIDE_MM = 130.0
    DESIRED_BORDER_WIDTH_BASE_MM = 5.0

    def __init__(
        self,
        base_image: PhrugalImage,
        target_aspect_ratio: float | Fraction | None = None,
        background_color: str = "white",
        text_color: str = "black",
        font_name: Optional[str] = DEFAULT_FONT,
    ):
        self.base_image = base_image
        self.background_color = getrgb(background_color)  # type: ColorTuple
        self.text_color = getrgb(text_color)  # type: ColorTuple
        self.font_name = font_name
        self.target_aspect_ratio = (
            target_aspect_ratio if target_aspect_ratio else Fraction(3, 2)
        )

    def get_decorated_image(self) -> PilImage.Image:
        needs_rotation = self.base_image.aspect_ratio < 1
        if needs_rotation:
            self.base_image.rotate_90_deg_ccw()

        image_dimensions_padded = self.get_padded_dimensions()
        decorated_img = PilImage.new(
            "RGB", image_dimensions_padded, color=self.background_color
        )
        x_border, y_border = self.get_border_dimensions()
        decorated_img.paste(
            self.base_image.pillow_image,
            scale_dimensions(self.get_border_dimensions(), 0.5),
        )

        # TODO: draw text

        return decorated_img

    def draw_text(self, image_w_border) -> None:
        draw = Draw(image_w_border)

    def _get_minimal_border_dimensions(self) -> Dimensions:
        x_dim_orginal, y_dim_orginal = self.base_image.image_dims

        # we target a 5mm border on each side a 13cm x 9cm print as a reference size
        # factor 2: we want the border on both sides of the image
        desired_border_ratio = (
            self.DESIRED_BORDER_WIDTH_BASE_MM * self.BORDER_MULTIPLIER * 2.0
        ) / self.NOMINAL_LEN_LARGER_SIDE_MM

        if x_dim_orginal > y_dim_orginal:
            x_border = desired_border_ratio * x_dim_orginal
            y_border = x_border
        else:
            y_border = desired_border_ratio * y_dim_orginal
            x_border = y_border

        return int(x_border), int(y_border)

    def get_border_dimensions(self):
        """Return border dimensions in pixel to hit the target aspect ratio.

        Note: the border dimensions will be always be for both borders, so the actual
        borders will e.g. have half of the returned value.
        """
        minimal_border_dimensions = self._get_minimal_border_dimensions()
        min_size_x, min_size_y = add_dimensions(
            minimal_border_dimensions, self.base_image.image_dims
        )
        current_aspect_ratio = min_size_x / min_size_y

        if current_aspect_ratio > self.target_aspect_ratio:
            # Image is wider than target aspect ratio
            new_height = min_size_x / self.target_aspect_ratio
            padding_y = new_height - min_size_y
            padding_x = 0
        else:
            # Image is taller than target aspect ratio
            new_width = min_size_y * self.target_aspect_ratio
            padding_x = new_width - min_size_x
            padding_y = 0

        extra_border_padding = padding_x, padding_y
        return add_dimensions(extra_border_padding, minimal_border_dimensions)

    def get_padded_dimensions(self) -> Dimensions:
        padded = add_dimensions(
            self.get_border_dimensions(), self.base_image.image_dims
        )
        padded = int(padded[0]), int(padded[1])  # ensure int as values
        return padded

    # def get_decorated_image(self, decoration: BorderDecorator) -> Image:
    #     new_img = Image.new(
    #         "RGB",
    #         decoration.get_size_with_border(self.image_dims),
    #         color=decoration.background_color,
    #     )
    #     new_img.paste(self._image, decoration.get_border_size(self.image_dims))
    #     self._draw_text(new_img, decoration)
    #
    #     return new_img

    # def _draw_text(self, img: Image, decoration: BorderDecorator) -> None:
    #     draw = ImageDraw.Draw(img)
    #     font = self._get_font(decoration)
    #     border_x, border_y = decoration.get_border_size(self.image_dims)
    #
    #     text = self._get_text()
    #     text_offset_pixel = int(
    #         (border_x - decoration.get_font_size(self.image_dims)) * 0.5
    #     )
    #     text_origin = (
    #         text_offset_pixel + border_x,
    #         text_offset_pixel + self.image_dims[1] + border_y,
    #     )
    #     draw.text(text_origin, text, fill=decoration.text_color, font=font)
    #
    # def _get_text(self) -> str:
    #     # 50mm | f/2.8 | 1/250s | ISO 400
    #     exif = PhrugalExifData(self.file_name)
    #
    #     candidates = [
    #         exif.get_focal_len(),
    #         exif.get_aperture(),
    #         exif.get_shutter_speed(),
    #         exif.get_iso(),
    #     ]
    #     t = " | ".join([x for x in candidates if x])
    #     return t
    #
    # def _get_font(self, decoration: BorderDecorator) -> ImageFont.FreeTypeFont:
    #     font_size = int(decoration.get_font_size(self.image_dims))
    #     if decoration.font is None:
    #         font = ImageFont.truetype("arial.ttf", size=font_size)
    #     else:
    #         font = ImageFont.truetype(decoration.font, size=font_size)
    #     return font

    def _get_font(self, font_name: str, font_size: int | None = None) -> str:
        if font_size is None:
            font_size = self.get_font_size()
        if (font_name, font_size) in self.FONT_CACHE:
            font = self.FONT_CACHE[(font_name, int(font_size))]
        else:
            font = truetype(font_name, size=font_size)
            self.FONT_CACHE[(font_name, int(font_size))] = font
        return font

    def get_font_size(self) -> int:
        dim_x, dim_y = self.get_border_dimensions()
        dim_smaller = min(dim_x, dim_y)
        # factor 2, since border size returns dimensions for both borders
        fs = (dim_smaller / 2) * self.TEXT_RATIO
        return int(fs)
