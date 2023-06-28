"""Helper function for plotting tiles."""
from typing import Tuple

import numpy as np

from src import np_tiles_converter


def get_tile_center_coords(
    tile_x_idx: int, tile_y_idx: int, zoom: int
) -> Tuple[float, float]:
    """Return coordinates of the tile center.

    Returns:
        lat: latitude of the tile center
        lon: longitude of the tile center
    """
    point_lat, point_lon = np_tiles_converter.np_idx2deg(
        tile_x_idx, tile_y_idx, zoom=zoom
    )

    return point_lat[0], point_lon[0]


def get_tile_box_coords(x_idx_tile: int, y_idx_tile: int, zoom: int) -> np.ndarray:
    """Return coordinates of the tile box.

    Arguments:
        x_idx_tile - integer
        y_idx_tile - integer

    Returns:
        tile_coord: array of floats, shape = [5,2], outputs 5 points with (lat, lon)
    """
    x_tile = x_idx_tile
    y_tile = y_idx_tile

    corner_points = [
        [x_tile, y_tile],
        [x_tile, y_tile + 1],
        [x_tile + 1, y_tile + 1],
        [x_tile + 1, y_tile],
        [x_tile, y_tile],  ## connects box back to the first point
    ]

    tile_box = np.array(corner_points)

    (tile16_lat_deg, tile16_lon_deg) = np_tiles_converter.np_idx2deg(
        tile_box[:, 0], tile_box[:, 1], zoom=zoom, offset=0
    )

    tile_box_coord: np.ndarray = np.concatenate(
        [tile16_lat_deg.reshape(-1, 1), tile16_lon_deg.reshape(-1, 1)], axis=1
    )

    return tile_box_coord
