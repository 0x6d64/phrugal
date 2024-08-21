from enum import StrEnum, unique, auto
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

from phrugal.composition import ImageComposition
from phrugal.decoration_config import DecorationConfig
from phrugal.image import PhrugalImage


@unique
class PaddingStrategy(StrEnum):
    PLACEHOLDER = auto()
    DUPLICATE = auto()
    UPSCALE = auto()


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
        self._img_instances: List[PhrugalImage] = []
        self.target_aspect_ratio = Fraction(target_aspect_ratio)
        self._image_groups: List[Tuple[PhrugalImage, ...]] | None = None

    def create_compositions(
        self,
        output_path: Path | str,
        images_count: int,
        padding_strategy: PaddingStrategy = PaddingStrategy.PLACEHOLDER,
    ):
        for in_file in self.input_files:
            img = PhrugalImage(in_file)
            self._img_instances.append(img)

        self._img_instances = sorted(
            self._img_instances, key=lambda x: x.aspect_ratio_normalized, reverse=False
        )
        self._generate_img_groups(self._img_instances, images_count)
        self._apply_padding_strategy(padding_strategy)
        self._process_all_img_groups(output_path)

    def _process_all_img_groups(self, output_path):
        for idx, group in enumerate(self._image_groups):
            composition_filename = output_path / self._get_filename(group, idx)
            composition = ImageComposition(
                group, target_aspect_ratio=self.target_aspect_ratio
            )
            composition.write_composition(
                filename=composition_filename, decoration_config=self.decoration_config
            )

    def _get_filename(self, group, idx):
        fn = Path(f"img-{idx}")
        return fn.with_suffix(".jpg")

    def _apply_padding_strategy(self, strategy: PaddingStrategy):
        if strategy == PaddingStrategy.UPSCALE:
            pass  # do nothing, upscaling happens automatically
        elif strategy == PaddingStrategy.PLACEHOLDER:
            raise NotImplementedError()  # fixme: implement!
        elif strategy == PaddingStrategy.DUPLICATE:
            raise NotImplementedError()  # fixme: implement!
        else:
            raise RuntimeError("unknown strategy!")

    def discover_images(self, path):
        self.input_files = [p for p in Path(path).glob("**/*.jpg")]

    def _generate_img_groups(
        self, input_objects: List[PhrugalImage], group_len: int
    ) -> None:
        """Split a list into tuples of size n (last remainder tuple can be smaller)."""
        img_grps = list(zip(*[input_objects[i:] for i in range(group_len)]))
        remainder = input_objects[len(img_grps) * group_len :]
        if remainder:
            img_grps.append(tuple(remainder))
        self._image_groups = img_grps
