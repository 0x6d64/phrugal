from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, List

import PIL.Image as pill_image
from PIL.Image import Image, Resampling

from phrugal.decorated_image import DecoratedPhrugalImage
from phrugal.decoration_config import DecorationConfig
from phrugal.image import PhrugalImage


@dataclass
class ImageMerge:
    image: Image
    count: int

    @property
    def x(self):
        return self.image.size[0]

    @property
    def y(self):
        return self.image.size[1]

    @property
    def aspect_ratio(self):
        x, y = self.image.size
        return float(x) / float(y)

    def ensure_landscape_orientation(self, rotate_ccw=True):
        is_landscape_orientation = self.aspect_ratio >= 1
        if not is_landscape_orientation:
            self.image = self.image.rotate(90 if rotate_ccw else -90, expand=True)

    def scale_to_target_dimensions(
        self,
        x_target: int | None = None,
        y_target: int | None = None,
        resample_method: Resampling = Resampling.LANCZOS,
    ) -> None:
        if x_target is None and y_target is None:
            raise RuntimeError("need either x or y dim")
        elif x_target is not None and y_target is not None:
            raise RuntimeError("most not give x and y dim")

        x_prev, y_prev = self.image.size
        if x_target:
            factor = float(x_target) / float(x_prev)
            y_target = y_prev * factor
        else:
            factor = float(y_target) / float(y_prev)
            x_target = x_prev * factor
        self.image.resize(
            (x_target, y_target), resample=resample_method, reducing_gap=4.0
        )


class ImageComposition:
    def __init__(
        self, images: Iterable[PhrugalImage], target_aspect_ratio: Fraction | float
    ):
        self.images = images
        self.target_aspect_ratio = target_aspect_ratio

    def write_composition(self, filename: Path, decoration_config: DecorationConfig):
        decorated_images = self._get_decorated_images(decoration_config)
        composition = self._get_composition(decorated_images)
        composition.save(filename)

    def _get_composition(self, decorated_images: Iterable[Image]) -> Image:
        composition = self._merge_image_list(
            [ImageMerge(image=im, count=1) for im in decorated_images]
        )
        return composition.image

    @staticmethod
    def _merge_image_list(image_data: List[ImageMerge]) -> ImageMerge | None:
        """Merge a list of images until you end up with one single image.

        As an input, we expect a list of tuples, each represent an image plus the count of images contained.
        The algorithm always merges the 2 images with the least number of images contained until only 1 image
        remains.

        :param image_data:
        :return:
        """
        if not image_data:
            return None
        if len(image_data) == 1:
            return image_data[0]
        image_data.sort(key=lambda i: i.count)
        new_merged = ImageComposition._merge_two_images(
            image_data.pop(0), image_data.pop(0)
        )
        image_data.append(new_merged)
        return ImageComposition._merge_image_list(image_data)

    @staticmethod
    def _merge_two_images(img_a: ImageMerge, img_b: ImageMerge) -> ImageMerge:
        img_a.ensure_landscape_orientation()
        img_b.ensure_landscape_orientation()

        # check that aspect ratios are the same (or close enough)
        accepted_delta = 1e-5
        ratio_diff = abs(img_a.aspect_ratio - img_b.aspect_ratio)
        assert ratio_diff < accepted_delta

        bigger_x_dim = max(img_a.image.size[0], img_b.image.size[0])
        img_a.scale_to_target_dimensions(x_target=bigger_x_dim)
        img_b.scale_to_target_dimensions(x_target=bigger_x_dim)

        new_img = pill_image.new(
            "RGB", (bigger_x_dim, img_a.y + img_b.y), color="white"
        )
        new_img.paste(img_a.image, (0, 0))
        new_img.paste(img_b.image, (0, img_a.y))

        new_count = img_a.count + img_b.count
        merge_returned = ImageMerge(image=new_img, count=new_count)
        merge_returned.ensure_landscape_orientation(
            rotate_ccw=(new_count / 2) % 2 == 0  # rotate cw and ccw every 2 merges
        )
        return merge_returned

    def _get_decorated_images(self, config: DecorationConfig) -> Iterable[Image]:
        decorated_images = []
        for image in self.images:
            img_decorated = DecoratedPhrugalImage(
                image, target_aspect_ratio=self.target_aspect_ratio
            )
            img_decorated.config = config
            decorated_images.append(img_decorated.get_decorated_image())
        return decorated_images

    def close_images(self):
        for image in self.images:
            image.close_image()
