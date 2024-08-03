import pprint
from pathlib import Path

import tabulate

import phrugal.image
import unittest


class TestPhrugal(unittest.TestCase):
    ENABLE_PRINTING = True

    def setUp(self):
        self.test_image_source = Path("./img/exif-data-testdata")

    def test_get_shutter_speed(self):
        input_fn = []
        results = []

        for img in self.test_image_source.glob("*.jpg"):
            filename_fragment = img.stem.replace("20240729_00", "")

            ped = phrugal.image.PhrugalExifData(img)
            result = ped.get_shutter_speed()

            input_fn.append(filename_fragment)
            results.append(result)

        if self.ENABLE_PRINTING:
            print(
                tabulate.tabulate(
                    zip(input_fn, results),
                    headers=("filename", "exif input"),
                )
            )
