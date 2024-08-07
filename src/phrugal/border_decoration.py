from typing import Optional

from PIL.ImageColor import getrgb

from . import ColorTuple, PixelTuple


class BorderDecoration:
    """Represents geometry of an image border and the text written on it"""

    TEXT_RATIO = 0.7  # how many percent of the border shall be covered by text

    def __init__(
        self,
        background_color: str = "white",
        text_color: str = "black",
        font: Optional[str] = None,
    ):
        self.background_color = getrgb(background_color)  # type: ColorTuple
        self.text_color = getrgb(text_color)  # type: ColorTuple
        self.font = font

    def get_border_size(self, image_dims: PixelTuple) -> PixelTuple:
        nominal_dimension_x_mm = 130
        nominal_dimension_y_mm = 90
        desired_border_width_mm = 5
        desired_border_ratio_x = desired_border_width_mm / nominal_dimension_x_mm
        desired_border_ratio_y = desired_border_width_mm / nominal_dimension_y_mm
        img_x, img_y = image_dims
        return (
            int(desired_border_ratio_x * img_x),
            int(desired_border_ratio_y * img_y),
        )

    def get_size_with_border(self, image_dims: PixelTuple) -> PixelTuple:
        border_dim = self.get_border_size(image_dims)
        result = tuple(2 * brd + im for brd, im in zip(border_dim, image_dims))
        return result

    def get_font_size(self, image_dims: PixelTuple) -> float:
        dim_x, dim_y = self.get_border_size(image_dims)
        dim_average = (dim_x + dim_y) / 2
        return dim_average * self.TEXT_RATIO
