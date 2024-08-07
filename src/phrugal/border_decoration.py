from typing import Optional

from PIL.Image import Image
from PIL.ImageColor import getrgb

from .image import PhrugalImage
from .types import ColorTuple, Dimensions


class BorderDecorator:
    """Represents geometry of an image border and the text written on it"""

    TEXT_RATIO = 0.7  # how many percent of the border shall be covered by text

    def __init__(
        self,
        base_image: PhrugalImage,
        background_color: str = "white",
        text_color: str = "black",
        font: Optional[str] = None,
    ):
        self.base_image = base_image
        self.background_color = getrgb(background_color)  # type: ColorTuple
        self.text_color = getrgb(text_color)  # type: ColorTuple
        self.font = font

    def get_decorated_image(self) -> Image:
        # TODO: real implementation
        return self.base_image.image

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

    def get_border_size(self, image_dims: Dimensions) -> Dimensions:
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

    def get_size_with_border(self, image_dims: Dimensions) -> Dimensions:
        border_dim = self.get_border_size(image_dims)
        result = tuple(2 * brd + im for brd, im in zip(border_dim, image_dims))
        return result

    def get_font_size(self, image_dims: Dimensions) -> float:
        dim_x, dim_y = self.get_border_size(image_dims)
        dim_average = (dim_x + dim_y) / 2
        return dim_average * self.TEXT_RATIO
