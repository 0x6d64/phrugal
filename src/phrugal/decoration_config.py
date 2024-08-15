from .exif import PhrugalExifData


class DecorationConfig:
    def __init__(self, item_separator: str = " | "):
        self.bottom_left = []
        self.bottom_right = []
        self.top_left = []
        self.top_right = []
        self.item_separator = item_separator

    def load_default_config(self):
        """Some default values, created mostly for debug purposes."""
        self.bottom_left = [
            # ("camera_model", {}),
            # ("lens_model", {}),
            ("focal_length", {}),
            ("aperture", {}),
            ("shutter_speed", {"use_nominal_value": True}),
            ("iso", {}),
        ]
        self.bottom_right = [
            ("gps_coordinates", {"use_dms": True}),
        ]
        self.top_left = [
            ("description", None),
        ]
        self.top_right = [
            ("timestamp", {"format": "%Y-%m-%dT%H:%M"}),
            ("geocode", {"zoom": 12}),
        ]

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
        self, exif: PhrugalExifData, configured_items: list
    ) -> str:
        result_fragments = []
        for item in configured_items:
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
