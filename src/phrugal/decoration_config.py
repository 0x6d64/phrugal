import json
from pathlib import Path

from .exif import PhrugalExifData


class DecorationConfig:
    DEFAULT_CONFIG = {
        "bottom_left": {
            "focal_length": {},
            "aperture": {},
            "shutter_speed": {"use_nominal_value": True},
            "iso": {},
        },
        "bottom_right": {
            "gps_coordinates": {"use_dms": True},
        },
        "top_left": {
            "description": {},
        },
        "top_right": {
            "timestamp": {"format": "%Y-%m-%dT%H:%M"},
            "geocode": {"zoom": 12},
        },
    }

    def __init__(self, item_separator: str = " | "):
        self.item_separator = item_separator
        self._config = dict()

    @property
    def bottom_left(self):
        return self._config.get("bottom_left")

    @property
    def bottom_right(self):
        return self._config.get("bottom_right")

    @property
    def top_left(self):
        return self._config.get("top_left")

    @property
    def top_right(self):
        return self._config.get("top_right")

    def load_from_file(self, config_file: Path | str):
        with open(config_file, "r") as cf:
            self._config = json.load(cf)

    def write_default_config(self, config_file: Path | str):
        self._write_config(config_file, self.DEFAULT_CONFIG)

    @staticmethod
    def _write_config(config_file: Path | str, config: dict):
        with open(config_file, "w") as cf:
            json.dump(config, cf, indent=4)

    def load_default_config(self):
        """Some default values, created mostly for debug purposes."""
        self._config = self.DEFAULT_CONFIG

    def get_string_at_corner(self, exif: PhrugalExifData, corner: str) -> str:
        if corner == "bottom_left":
            result_string = self._build_configured_string(exif, self.bottom_left)
        elif corner == "bottom_right":
            result_string = self._build_configured_string(exif, self.bottom_right)
        elif corner == "top_left":
            result_string = self._build_configured_string(exif, self.top_left)
        elif corner == "top_right":
            result_string = self._build_configured_string(exif, self.top_right)
        else:
            raise ValueError(f"Corner name {corner} is not valid")
        return result_string

    def _build_configured_string(
        self, exif: PhrugalExifData, configured_items: dict
    ) -> str:
        result_fragments = []
        for item in configured_items.items():
            item_name, item_config_params = item
            exif_getter_name = f"get_{item_name}"
            if not hasattr(exif, exif_getter_name):
                raise ValueError(f"item {item_name} not implemented")
            getter = getattr(exif, exif_getter_name)
            if item_config_params:
                single_fragment = getter(**item_config_params)
            else:
                single_fragment = getter()
            result_fragments.append(single_fragment)
        return self.item_separator.join((x for x in result_fragments if x))
