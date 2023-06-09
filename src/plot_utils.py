import numpy as np
from src import np_tiles_converter

def get_tile_box_coords(x_idx_tile: int, 
                        y_idx_tile: int,
                        zoom: int) -> np.ndarray:
    """Return coordinates of the tile box.

    Arguments:
        x_idx_tile - integer
        y_idx_tile - integer

    Returns:
        tile_coord: array of floats, shape = [5,2], outputs 5 points with (lat, lon)
    """
    x_tile = x_idx_tile
    y_tile = y_idx_tile

    tile_box = [[x_tile, y_tile],
            [x_tile, y_tile+1],
            [x_tile+1, y_tile+1],
            [x_tile+1, y_tile],
            [x_tile, y_tile], ## connects box back to the first point
           ]

    tile_box = np.array(tile_box)
    (tile16_lat_deg, 
     tile16_lon_deg) = np_tiles_converter.np_idx2deg(tile_box[:,0], 
                                                    tile_box[:,1], 
                                                    zoom = zoom,
                                                    offset=0)

    tile_coord = np.concatenate([tile16_lat_deg.reshape(-1,1), tile16_lon_deg.reshape(-1,1)],axis=1)    

    return tile_coord