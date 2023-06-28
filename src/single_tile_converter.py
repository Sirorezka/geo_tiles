import math
import numpy as np

from typing import Union, Dict, Tuple


def zoom_power(zoom: int) -> float:
    max_zoom = 22

    # clipping zoom between 0 and 19
    zoom = np.clip(zoom, 0, max_zoom)
    return 2.0**zoom


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    """Converts degrees of longitude and latitude to x,y tile coordinates.

    This function is non-vectorized version. Just a simple example how to use the formula.

    Returns two integer numbers that represent tiles x and y coordinates.
    Function breaks whole world map into tiles such that
    top right corner will have coordinates (0,0) and bottom left
    corner coordinates (2**zoom-1, 2**zoom-1)

    Arguments:
    lon_deg: degrees of longitude, must be between [-179.999 and 179.999]
    lat_deg: degrees of latitude, must be between [-85.051129 and 85.051129]
    zoom: integer value, defines tiles granularity.
        zoom = 0 - single tile (1 tile) covers whole world
        zoom = 12 - 4096 x 4096 tiles
        zoom = 22 - proposed maximum, tiles are aproximately 10x10 meters

    Returns:
        xtile - integer, tile x coordinate
        ytile - integer, tile y coordinate

    Sources:
        -- https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """
    max_lon = 179.999
    max_lat = 85.05

    assert -180 <= lon_deg <= 180
    assert -90 <= lat_deg <= 90

    # clipping to maximum lon and lat
    lon_deg = max(-max_lon, min(max_lon, lon_deg))
    lat_deg = max(-max_lat, min(max_lat, lat_deg))

    # converting to radians
    lon_rad = math.radians(lon_deg)
    lat_rad = math.radians(lat_deg)
    n = zoom_power(zoom)

    # tiles formula
    xtile = math.floor((lon_rad + math.pi) / (2 * math.pi) * n)
    ytile = math.floor(
        (math.pi - math.log(math.tan(lat_rad / 2 + math.pi / 4))) / (math.pi * 2.0) * n
    )
    return (xtile, ytile)
