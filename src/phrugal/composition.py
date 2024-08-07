from pathlib import Path
from typing import Iterable

from PIL.Image import Image

import phrugal.border_decoration
from phrugal.image import PhrugalImage


class ImageComposition:
    def __init__(self, images: Iterable[PhrugalImage]):
        self.images = images

    def write_composition(self, filename: Path):
        decorated_images = self._get_decorated_images()
        # TODO: arrange images into new image
        # TODO: write images out

    def _get_decorated_images(self) -> Iterable[Image]:
        decorated_images = []
        for image in self.images:
            decorator = phrugal.border_decoration.BorderDecorator(image)
            decorated_images.append(decorator.get_decorated_image())
        return decorated_images

    def close_images(self):
        for image in self.images:
            image.close_image()
