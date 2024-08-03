from pathlib import Path

import phrugal.exif
import phrugal.image
import unittest


class TestPhrugal(unittest.TestCase):
    ENABLE_PRINTING = False

    @classmethod
    def setUpClass(cls):
        cls.test_image_source = Path("./img/exif-data-testdata").glob("**/*.jpg")
        cls.test_instances = [
            phrugal.exif.PhrugalExifData(x) for x in cls.test_image_source
        ]

    def _get_specific_img_instance(self, file_substring):
        return next(
            (x for x in self.test_instances if file_substring in x.image_path.name),
            None,
        )

    def test_get_focal_len(self):
        input_and_expected = [
            ("0027", "24mm"),
            ("0095", "0mm"),
        ]
        for img, expected in input_and_expected:
            instance = self._get_specific_img_instance(img)
            actual = instance.get_focal_len()
            self.assertEqual(expected, actual)
            if self.ENABLE_PRINTING:
                print(instance.image_path.stem, actual)

    def test_get_aperture(self):
        input_and_expected = [
            ("0027", "f/4.0"),
            ("0095", "inf"),
        ]
        for img, expected in input_and_expected:
            instance = self._get_specific_img_instance(img)
            actual = instance.get_aperture()
            self.assertEqual(expected, actual)
            if self.ENABLE_PRINTING:
                print(instance.image_path.stem, actual)

    def test_get_iso(self):
        input_and_expected = [
            ("0027", "ISO 400"),
            ("0028", "ISO 320"),
            ("0040", "ISO 100"),
            ("0047", "ISO 100"),
            ("0095", "ISO 4000"),
        ]
        for img, expected in input_and_expected:
            instance = self._get_specific_img_instance(img)
            actual = instance.get_iso()
            self.assertEqual(expected, actual)
            if self.ENABLE_PRINTING:
                print(instance.image_path.stem, actual)

    def test_get_shutter_speed(self):
        # fmt: off
        expected_results = {'1.3s', '1/60s', '1/40s', '1/800s', '1/30s', '1/1250s', '1/500s', '1/25s',
                            '1/640s', '1/80s', '1/125s', '1/50s', '1/8s', '0.6s', '0.8s', '1/2000s',
                            '2.0s', '1/3s', '1/1600s', '1/100s', '1/160s', '1/400s', '1/6s', '1/15s',
                            '1/13s', '1/10s', '1/320s', '1.0s', '1.6s', '1/250s', '1/20s', '1/200s',
                            '1/5s', '1/1000s', '3.2s', '1/2500s', '1/2s', '1/4s'}
        # fmt: on

        for ped in self.test_instances:
            ped = phrugal.exif.PhrugalExifData(ped.image_path)
            actual = ped.get_shutter_speed()
            self.assertIn(actual, expected_results)

            if self.ENABLE_PRINTING:
                print(ped.image_path.stem, actual)
