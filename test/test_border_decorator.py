from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from phrugal.border_decorator import BorderDecorator
from phrugal.image import PhrugalImage


class TestBorderDecorator(TestCase):
    def setUp(self):
        self.test_data_path = Path("./img/aspect-ratio")
        self._temp_dir = TemporaryDirectory(prefix="phrugal-test")
        self.temp_path = Path(self._temp_dir.name)

        self.img_path_landscape_extreme = self.test_data_path / "100x600.jpg"
        self.img_path_portrait_extreme = self.test_data_path / "100x600.jpg"
        self.img_path_square = self.test_data_path / "400x400.jpg"
        self.img_path_landscape_regular = self.test_data_path / "600x400.jpg"
        self.img_path_portrait_regular = self.test_data_path / "400x600.jpg"

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_constructor(self):
        base_img = PhrugalImage(self.img_path_portrait_extreme)
        __ = BorderDecorator(base_img)

    def test_get_padded_dimensions(self):
        base_images = [
            (self.img_path_square, None),
            (self.img_path_landscape_regular, None),
            (self.img_path_landscape_extreme, None),
            (self.img_path_portrait_regular, None),
            (self.img_path_portrait_extreme, None),
        ]

        target_aspect_ratios = [1.0, 4.0 / 3.0, 0.5]

        for t_ar in target_aspect_ratios:
            for bi, expectation in base_images:
                base_img = PhrugalImage(bi)
                decorator = BorderDecorator(base_img, target_aspect_ratio=t_ar)
                padded_dimensions = decorator.get_padded_dimensions()
                actual_ratio = padded_dimensions[0] / padded_dimensions[1]
                test_parameters = (
                    f"target ar: {t_ar}, actual ar: {actual_ratio}, image: {bi}"
                )
                self.assertAlmostEqual(
                    t_ar, actual_ratio, 7, msg=f"fail at {test_parameters}"
                )
