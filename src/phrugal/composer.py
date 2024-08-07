from fractions import Fraction
from pathlib import Path
from typing import List, Tuple, TypeVar

from phrugal.composition import ImageComposition
from phrugal.image import PhrugalImage

T = TypeVar("T")


class PhrugalComposer:
    DEFAULT_ASPECT_RATIO = Fraction(4, 3)

    def __init__(
        self,
        input_files=None,
        target_aspect_ratio: Fraction | float = DEFAULT_ASPECT_RATIO,
    ):
        self.input_files = input_files
        self._img_instances = []
        self.target_aspect_ratio = Fraction(target_aspect_ratio)

    def create_compositions(self, output_path: Path | str, images_count: int):
        """Does the following:

        - read the image metadata of the input files
        - figure out the images that go together in a single composition
        - for each composition: create it, and write the output into the output folder
        - after that, free the space of that composition

        - For each picture in the input, calculate the aspect ratio
            - if the aspect ratio is >1, calculate 1/aspect ratio (to normalize it)
        - sort the images by aspect ratio
        - do groups for N images
        - for each of the groups:
            - do all combinations of orders of images
            - for each combination: create score for the fit
                - todo: how can we assess the fit as a score?
            - then: select best, trigger actual creation of the image


        """
        for in_file in self.input_files:
            img = PhrugalImage(in_file)
            self._img_instances.append(img)

        self._img_instances = sorted(
            self._img_instances, key=lambda x: x.aspect_ratio_normalized, reverse=True
        )

        img_groups = self.generate_tuples(self._img_instances, images_count)
        for group in img_groups:
            composition_filename = (
                output_path / "-".join(x.file_name.stem for x in group)
            ).with_suffix(".jpg")
            composition = ImageComposition(group)
            composition.write_composition(filename=composition_filename)
        print(img_groups)

    def discover_images(self, path):
        self.input_files = [p for p in Path(path).glob("**/*.jpg")]

    @staticmethod
    def generate_tuples(objects: List[T], n: int) -> List[Tuple[T, ...]]:
        result = list(zip(*[objects[i:] for i in range(n)]))
        remainder = objects[len(result) * n :]
        if remainder:
            result.append(tuple(remainder))
        return result
