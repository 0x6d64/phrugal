from fractions import Fraction
from pathlib import Path
from typing import Iterable

from PIL.Image import Image

from phrugal.decorated_image import DecoratedPhrugalImage
from phrugal.decoration_config import DecorationConfig
from phrugal.image import PhrugalImage


class ImageComposition:
    def __init__(
        self, images: Iterable[PhrugalImage], target_aspect_ratio: Fraction | float
    ):
        self.images = images
        self.target_aspect_ratio = target_aspect_ratio

    def write_composition(self, filename: Path, decoration_config: DecorationConfig):
        decorated_images = self._get_decorated_images(decoration_config)
        # TODO: arrange images into new image
        # TODO: write images out

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
