class DecorationConfig:
    def __init__(self):
        self.bottom_left = []
        self.bottom_right = []
        self.top_left = []
        self.top_right = []

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
        # TODO
        result_string = ""
        for item in configured_items:
            pass

        return result_string
