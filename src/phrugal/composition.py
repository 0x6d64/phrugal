from pathlib import Path
from typing import Iterable

from phrugal.image import PhrugalImage


class ImageComposition:
    def __init__(self, images: Iterable[PhrugalImage]):
        self.images = images

    def write_composition(self, filename: Path):
        pass

    def close_images(self):
        for image in self.images:
            image.close_image()
