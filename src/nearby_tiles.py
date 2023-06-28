from src import geometry_converter, np_tiles_converter
import numpy as np
import pandas as pd
from typing import Tuple


def get_nearby_tiles(
    df_coords: pd.DataFrame, zoom: int, radius: float = 500
) -> pd.DataFrame:
    """Output all tiles in given distance from provided coordinates.

    For example if you have 100 locations and for each point you want to list
    all tiles which have centers in aprx 500 meters.

    Arguments:
        df_coords - have two columns "lon" and "lat" which store coordinates in degrees
        radius - radius in meters

    """

    assert "lon" in df_coords.columns
    assert "lat" in df_coords.columns
    assert radius > 0
    assert zoom >= 1 and zoom <= 23

    # we will need to add ids to all coordinates:
    n_coords = df_coords.shape[0]

    if n_coords > 30000:
        print("Too many points in dataset, calculations may take a while")

    coord_lat = df_coords["lat"].values
    coord_lon = df_coords["lon"].values
    coord_id = np.ogrid[:n_coords]  ## simply indexing [0,1,2,3,4,...]

    # for each input coordinate
    # 1. get it's tile X,Y indexes
    # 2. tile center lat/lot coordinates
    idx_x_cent, idx_y_cent = np_tiles_converter.np_deg2idx(
        coord_lat, coord_lon, zoom=zoom
    )
    center_lat, center_lon = np_tiles_converter.np_idx2deg(
        idx_x_cent, idx_y_cent, zoom=zoom
    )

    # distance in meters to the closest adjacent tile
    lat_adj, lon_adj = np_tiles_converter.np_idx2deg(
        idx_x_cent + 1, idx_y_cent, zoom=zoom
    )
    x_tile_dist = np_tiles_converter.np_haversin(
        center_lat, center_lon, lat_adj, lon_adj
    )

    lat_adj, lon_adj = np_tiles_converter.np_idx2deg(
        idx_x_cent, idx_y_cent + 1, zoom=zoom
    )
    y_tile_dist = np_tiles_converter.np_haversin(
        center_lat, center_lon, lat_adj, lon_adj
    )

    # let's calculate how far we should searh for good tiles
    # left, right, down and up from given points
    # we will include all tiles in 'lim' from current tile
    # adding small number to prevent division on zero
    x_tiles_lim = np.ceil(radius / x_tile_dist + 0.0001) + 1
    y_tiles_lim = np.ceil(radius / (y_tile_dist + 0.0001)) + 1

    max_x_lim = x_tiles_lim.max()
    max_y_lim = y_tiles_lim.max()
    max_xy = np.max([x_tiles_lim, y_tiles_lim], axis=0)  # max among x and y

    # To get full circle in given radius we need to check all nearby tiles:
    # by applying negative shifts (moving left/up) and positive shifts (moving right/down)
    # Because search is symmetric, let's only search one quarter of the circle
    # by checking only positive shifts
    shifts_xy = geometry_converter._xy_combinations(
        np.ogrid[: max_x_lim + 1],
        np.ogrid[: max_y_lim + 1],
    )
    shifts_xy = shifts_xy.astype(np.int32)
    n_shifts = shifts_xy.shape[0]

    # five columns: id, lat, lon, idx_x, idx_y
    center_coords = np.concatenate(
        [
            coord_id.reshape([-1, 1]),
            center_lat.reshape([-1, 1]),
            center_lon.reshape([-1, 1]),
            idx_x_cent.reshape([-1, 1]),
            idx_y_cent.reshape([-1, 1]),
        ],
        axis=1,
    )

    coords = np.repeat(center_coords, n_shifts, axis=0)

    # print (coords.shape)

    # same as np.repeat, but work a bit different
    shifts_x = np.tile(shifts_xy[:, 0], n_coords)
    shifts_y = np.tile(shifts_xy[:, 1], n_coords)

    # rough filter by delta tiles, given diagonal in the triangle
    #
    filter_rough = shifts_x + shifts_y <= max(max_x_lim, max_y_lim) * np.sqrt(2)
    coords = coords[filter_rough]
    shifts_x = shifts_x[filter_rough]
    shifts_y = shifts_y[filter_rough]

    # print (coords.shape)

    # all tiles candidates in required distance from given tile
    #
    inner_lat, inner_lon = np_tiles_converter.np_idx2deg(
        coords[:, 3] + shifts_x, coords[:, 4] + shifts_y, zoom=zoom
    )

    # calculate haversine distance and filter based on distance
    dist = np_tiles_converter.np_haversin(
        coords[:, 1], coords[:, 2], inner_lat, inner_lon
    )

    filt_dist = dist <= radius
    coords = coords[filt_dist]
    shifts_x = shifts_x[filt_dist]
    shifts_y = shifts_y[filt_dist]

    # print (coords.shape)

    nbr_id, nbr_x, nbr_y = _cover_full_circle(coords, shifts_x, shifts_y)

    nearby_tiles = pd.DataFrame(
        {
            "coord_id": nbr_id,
            "tile_idx_x": nbr_x,
            "tile_idx_y": nbr_y,
        }
    )

    return nearby_tiles


def _cover_full_circle(
    coords: np.ndarray, shifts_x: np.ndarray, shifts_y: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extrapolating shifts from circle Q1 to other quarters.
    """
    # neighbours in given distance
    nbr_id = np.array([])
    nbr_x = np.array([])
    nbr_y = np.array([])

    near_x = coords[:, 3] + 1 * shifts_x
    near_y = coords[:, 4] + 1 * shifts_y
    nbr_id = np.concatenate([nbr_id, coords[:, 0]])
    nbr_x = np.concatenate([nbr_x, near_x])
    nbr_y = np.concatenate([nbr_y, near_y])

    # to prevent duplication remove [0,0]
    filt = (shifts_x == 0) & (shifts_y == 0)
    shifts_x = shifts_x[~filt]
    shifts_y = shifts_y[~filt]
    coords = coords[~filt]

    near_x = coords[:, 3] + -1 * shifts_x
    near_y = coords[:, 4] + -1 * shifts_y
    nbr_id = np.concatenate([nbr_id, coords[:, 0]])
    nbr_x = np.concatenate([nbr_x, near_x])
    nbr_y = np.concatenate([nbr_y, near_y])

    # to prevent duplication remove [0,*] and [*,0]
    filt = (shifts_x == 0) | (shifts_y == 0)
    shifts_x = shifts_x[~filt]
    shifts_y = shifts_y[~filt]
    coords = coords[~filt]

    near_x = coords[:, 3] + -1 * shifts_x
    near_y = coords[:, 4] + 1 * shifts_y
    nbr_id = np.concatenate([nbr_id, coords[:, 0]])
    nbr_x = np.concatenate([nbr_x, near_x])
    nbr_y = np.concatenate([nbr_y, near_y])

    near_x = coords[:, 3] + 1 * shifts_x
    near_y = coords[:, 4] + -1 * shifts_y
    nbr_id = np.concatenate([nbr_id, coords[:, 0]])
    nbr_x = np.concatenate([nbr_x, near_x])
    nbr_y = np.concatenate([nbr_y, near_y])

    return nbr_id, nbr_x, nbr_y
