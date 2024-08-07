from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .types import Dimensions

MM_PER_INCH = 25.4


@dataclass
class PhrugalImage:
    def __init__(self, file_name: Path | str) -> None:
        self.file_name = Path(file_name)
        self.image = Image.open(self.file_name, mode="r")

    @property
    def image_dims(self) -> Dimensions:
        return self.image.size

    @property
    def aspect_ratio(self) -> float:
        """y_dim / x_dim"""
        x_dim, y_dim = self.image_dims
        return float(x_dim) / float(y_dim)

    @property
    def aspect_ratio_normalized(self) -> float:
        """Same as aspect ratio, but assume that we rotate portrait orientation to landscape always"""
        return self.aspect_ratio if self.aspect_ratio > 1 else 1 / self.aspect_ratio

    def close_image(self):
        self.image.close()

    def __repr__(self):
        return f"{self.file_name.name}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.image.close()
        return False

    def __del__(self):
        self.image.close()
