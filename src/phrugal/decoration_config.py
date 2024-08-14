from pathlib import Path

from .exif import PhrugalExifData



class DecorationConfig:
    def __init__(self, image: Path | str | None = None):
        self.bottom_left = []
        self.bottom_right = []
        self.top_left = []
        self.top_right = []
        self.image: Path | str = image
        self._exif: PhrugalExifData | None = None

    @property
    def exif(self):
        if self._exif is None:
            self._exif = PhrugalExifData(self.image)
        return self._exif

    def load_default_config(self):
        """Some default values, created mostly for debug purposes."""
        self.bottom_left = [
            ("focal_length", {}),
            ("aperture", {}),
            ("shutter_speed", {}),
            ("iso", {}),
        ]
        self.bottom_right = [
            ("gps_coordinates", {}),
        ]
        self.top_left = [
            ("description", None),
        ]
        self.top_right = [
            ("geocode", {"zoom": 12}),
        ]

    def get_string_at_position(self, position: str) -> str:
        if position == "bottom_left":
            result_string = self._get_configured_string(self.bottom_left)
        elif position == "bottom_right":
            result_string = self._get_configured_string(self.bottom_right)
        elif position == "top_left":
            result_string = self._get_configured_string(self.top_left)
        elif position == "top_right":
            result_string = self._get_configured_string(self.top_right)
        else:
            raise ValueError(f"Position {position} is not valid")
        return result_string


    def _get_configured_string(self, configured_items: list) -> str:
        result_fragments = []
        item_separator = " | "
        for item in configured_items:
            item_name, item_config_params = item
            exif_getter_name = f"get_{item_name}"
            if not hasattr(self.exif, exif_getter_name):
                raise ValueError(f"item {item_name} not implemented")
            getter = getattr(self.exif, exif_getter_name)
            single_fragment = getter()
            result_fragments.append(single_fragment)
        return item_separator.join((x for x in result_fragments if x))
