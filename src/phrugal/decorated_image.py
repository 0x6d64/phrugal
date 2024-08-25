import logging
from fractions import Fraction
from typing import Optional

import PIL.Image as PilImage
from PIL.ImageColor import getrgb
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype, FreeTypeFont

from .decoration_config import DecorationConfig
from .exif import PhrugalExifData
from .image import PhrugalImage
from .types import ColorTuple, Dimensions, Coordinates

logger = logging.getLogger(__name__)


def add_dimensions(a: Dimensions, b: Dimensions) -> Dimensions:
    assert len(a) == len(b) == 2
    a_x, a_y = a
    b_x, b_y = b
    return int(a_x + b_x), int(a_y + b_y)


def subtract_dimensions(a: Dimensions, b: Dimensions) -> Dimensions:
    assert len(a) == len(b) == 2
    a_x, a_y = a
    b_x, b_y = b
    return int(a_x - b_x), int(a_y - b_y)


def scale_dimensions(d: Dimensions, scale: float) -> Dimensions:
    x, y = d
    new_dim = int(x * scale), int(y * scale)
    return new_dim


class DecoratedPhrugalImage:
    """Represents geometry of an image border and the text written on it"""

    TEXT_RATIO = 0.7  # how many percent of the border shall be covered by text
    FONT_CACHE = dict()
    BORDER_MULTIPLIER = 1.0
    NOMINAL_LEN_LARGER_SIDE_MM = 130.0
    DESIRED_BORDER_WIDTH_BASE_MM = 5.0
    CORNER_NAMES = ["bottom_left", "bottom_right", "top_left", "top_right"]

    def __init__(
        self,
        base_image: PhrugalImage,
        target_aspect_ratio: float | Fraction | None = None,
        background_color: str = "white",
        text_color: str = "black",
        decoration_config: DecorationConfig | None = None,
    ):
        self.base_image = base_image
        self.background_color = getrgb(background_color)  # type: ColorTuple
        self.text_color = getrgb(text_color)  # type: ColorTuple
        self.target_aspect_ratio = (
            target_aspect_ratio if target_aspect_ratio else Fraction(3, 2)
        )
        self.config = decoration_config
        self._exif = None  # type: PhrugalExifData | None

    @property
    def exif(self):
        if self._exif is None:
            self._exif = PhrugalExifData(self.base_image.file_name)
        return self._exif

    def get_decorated_image(self) -> PilImage.Image:
        logger.debug(f"creating decorated image {self}")
        needs_rotation = self.base_image.aspect_ratio < 1.0
        if needs_rotation:
            logger.debug("rotating image...")
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
        logger.debug("drawing text on border...")
        self.draw_text_items(decorated_img)
        return decorated_img

    def draw_text_items(self, image_w_border) -> None:
        """Write all the configured text into the borders.

        This modification is in-place.
        """
        draw = Draw(image_w_border)
        font = self._get_font(self.config.get_font_name())
        for corner in self.CORNER_NAMES:
            text_on_right_side = corner.endswith("_right")
            # see https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#specifying-an-anchor
            text_anchor = "rd" if text_on_right_side else "ld"

            string_to_draw = self.config.get_string_at_corner(self.exif, corner)
            coordindates_for_draw = self._get_text_origin(corner)
            draw.text(
                coordindates_for_draw,
                string_to_draw,
                fill=self.text_color,
                font=font,
                anchor=text_anchor,
            )

    def _get_text_origin(self, corner: str) -> Coordinates:
        font_size = self.get_font_size()
        single_border_dims = scale_dimensions(self.get_border_dimensions(), 0.5)
        single_x_border, single_y_border = single_border_dims

        border_text_to_edge = (min(*single_border_dims) - font_size) / 2
        image_x_dim, image_y_dim = self.base_image.image_dims

        if corner == "bottom_left":
            x_pos = single_x_border + border_text_to_edge
            y_pos = 2 * single_y_border + image_y_dim - border_text_to_edge
        elif corner == "bottom_right":
            x_pos = single_x_border + image_x_dim - border_text_to_edge
            y_pos = 2 * single_y_border + image_y_dim - border_text_to_edge
        elif corner == "top_left":
            x_pos = single_x_border + border_text_to_edge
            y_pos = single_y_border - border_text_to_edge
            pass
        elif corner == "top_right":
            x_pos = single_x_border + image_x_dim - border_text_to_edge
            y_pos = single_y_border - border_text_to_edge
            pass
        else:
            raise ValueError(f"Corner name {corner} is not valid")
        return x_pos, y_pos

    def _get_minimal_border_dimensions(self) -> Dimensions:
        x_dim_original, y_dim_original = self.base_image.image_dims

        # we target a 5mm border on each side a 13cm x 9cm print as a reference size
        # factor 2: we want the border on both sides of the image
        desired_border_ratio = (
            self.DESIRED_BORDER_WIDTH_BASE_MM * self.BORDER_MULTIPLIER * 2.0
        ) / self.NOMINAL_LEN_LARGER_SIDE_MM

        if x_dim_original > y_dim_original:
            x_border = desired_border_ratio * x_dim_original
            y_border = x_border
        else:
            y_border = desired_border_ratio * y_dim_original
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

    def _get_font(self, font_name: str, font_size: int | None = None) -> FreeTypeFont:
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
