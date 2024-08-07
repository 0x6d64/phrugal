from fractions import Fraction
from pathlib import Path
from typing import Iterable

from PIL.Image import Image

from phrugal.border_decorator import BorderDecorator
from phrugal.image import PhrugalImage


class ImageComposition:
    def __init__(
        self, images: Iterable[PhrugalImage], target_aspect_ratio: Fraction | float
    ):
        self.images = images
        self.target_aspect_ratio = target_aspect_ratio

    def write_composition(self, filename: Path):
        decorated_images = self._get_decorated_images()
        # TODO: arrange images into new image
        # TODO: write images out

    def _get_decorated_images(self) -> Iterable[Image]:
        decorated_images = []
        for image in self.images:
            decorator = BorderDecorator(
                image, target_aspect_ratio=self.target_aspect_ratio
            )
            decorated_images.append(decorator.get_decorated_image())
        return decorated_images

    def close_images(self):
        for image in self.images:
            image.close_image()
