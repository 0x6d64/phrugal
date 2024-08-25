import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from phrugal.composer import PhrugalComposer
from phrugal.decoration_config import DecorationConfig


class TestPhrugalComposer(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        self.test_data_path = Path(f"{current_dir}/img/aspect-ratio")
        self.test_data_path = Path(f"{current_dir}/img/aspect-ratio")
        self.assertTrue(self.test_data_path.exists())
        self._temp_dir = TemporaryDirectory(prefix="phrugal-test")
        self.temp_path = Path(self._temp_dir.name)
        self.deco_config = DecorationConfig()
        self.deco_config.load_default_config()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_constructor(self):
        composer = PhrugalComposer(decoration_config=self.deco_config)
        self.assertAlmostEqual(4.0 / 3.0, composer.target_aspect_ratio)

        composer = PhrugalComposer(
            decoration_config=self.deco_config, target_aspect_ratio=0.1
        )
        self.assertAlmostEqual(0.1, composer.target_aspect_ratio)

    def test_discover_images(self):
        composer = PhrugalComposer(decoration_config=self.deco_config)
        composer.discover_images(self.test_data_path)
        expected_endings = [
            "100x600.jpg",
            "300x450.jpg",
            "360x240.jpg",
            "400x400.jpg",
            "400x600.jpg",
            "600x100.jpg",
            "600x400.jpg",
            "600x500.jpg",
            "600x600.jpg",
        ]
        found_input_files = [x.name for x in composer.input_files]
        for exp_input in expected_endings:
            with self.subTest(f"check expected {exp_input}"):
                self.assertIn(exp_input, found_input_files)

    def test_create_composition(self):
        composer = PhrugalComposer(decoration_config=self.deco_config)
        composer.discover_images(self.test_data_path)
        composer.create_compositions(output_path=self.temp_path)
