import _version
from . import _version

__version__ = _version.get_versions()["version"]

ColorTuple = tuple[int, int, int] | tuple[int, int, int, int]
PixelTuple = tuple[int, int]
