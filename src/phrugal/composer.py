from fractions import Fraction
from pathlib import Path
from typing import List, Tuple, TypeVar

from phrugal.composition import ImageComposition
from phrugal.decoration_config import DecorationConfig
from phrugal.image import PhrugalImage

T = TypeVar("T")


class PhrugalComposer:
    DEFAULT_ASPECT_RATIO = Fraction(4, 3)

    def __init__(
        self,
        decoration_config: DecorationConfig,
        input_files=None,
        target_aspect_ratio: Fraction | float = DEFAULT_ASPECT_RATIO,
    ):
        self.decoration_config = decoration_config
        self.input_files = input_files
        self._img_instances = []
        self.target_aspect_ratio = Fraction(target_aspect_ratio)

    def create_compositions(
        self,
        output_path: Path | str,
        images_count: int,
        padding_strategy: str = "placeholder",
    ):
        self._validate_padding_strategy(padding_strategy)

        for in_file in self.input_files:
            img = PhrugalImage(in_file)
            self._img_instances.append(img)

        self._img_instances = sorted(
            self._img_instances, key=lambda x: x.aspect_ratio_normalized, reverse=True
        )

        img_groups = self._generate_img_groups(self._img_instances, images_count)
        self._process_img_group(img_groups, output_path)

    def _process_img_group(self, img_groups, output_path):
        for group in img_groups:
            composition_filename = (
                output_path / "-".join(x.file_name.stem for x in group)
            ).with_suffix(".jpg")
            composition = ImageComposition(
                group, target_aspect_ratio=self.target_aspect_ratio
            )
            composition.write_composition(
                filename=composition_filename, decoration_config=self.decoration_config
            )

    @staticmethod
    def _validate_padding_strategy(padding_strategy):
        if padding_strategy == "placeholder":
            pass
        elif padding_strategy == "duplicate":
            raise NotImplementedError("not yet implemented")
        elif padding_strategy == "upscale":
            raise NotImplementedError("not yet implemented")
        else:
            raise RuntimeError(f"don't know padding strategy {padding_strategy}")

    def discover_images(self, path):
        self.input_files = [p for p in Path(path).glob("**/*.jpg")]

    @staticmethod
    def _generate_img_groups(
        input_objects: List[T], group_len: int
    ) -> List[Tuple[T, ...]]:
        """Split a list into tuples of size n (last remainder tuple can be smaller)."""
        result = list(zip(*[input_objects[i:] for i in range(group_len)]))
        remainder = input_objects[len(result) * group_len :]
        if remainder:
            result.append(tuple(remainder))
        return result
