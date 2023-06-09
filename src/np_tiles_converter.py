import math
import numpy as np

from typing import Union, Dict


def _check_if_float(val: Union[np.ndarray, float]) -> bool:
    """Checks if value is array or float.
    Returns 'True' if the passed variable is a single float/integer,
    otherwise returns False
    """
    if isinstance(val, (float, int, np.int64, np.float64, np.float32, np.float16)):
        return True
    else:
        return False
    
def zoom_power(zoom: int):
    """Zoom parameter defines tiles granularity.

    Zoom of 22 allows to have precision of less than 5 meters which is very much enough
    for most of the tasks.
    """

    max_zoom = 22
    zoom = np.clip(zoom, 0, max_zoom)
    return 2.0 ** zoom


def np_deg2idx(lat_deg: Union[np.ndarray, float], 
               lon_deg: Union[np.ndarray, float], 
               zoom: int) -> (Union[np.ndarray, float], Union[np.ndarray, float]):
    """Converts degrees of longitude and latitude to x,y tile coordinates.
    
    This function is numpy vectorized version. 
    
    Returns array with two integer numbers for each input. 
    This numbers represent x and y tiles coordinates.
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
        xtile - numpy array of integers, tile x coordinate 
        ytile - numpy array of integers, tile y coordinate
        
    Sources:
        -- https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """

    is_single = False # should we return array or single number
    if _check_if_float(lat_deg):
        lat_deg = np.array([lat_deg])
        is_single = True

    if _check_if_float(lon_deg):
        lon_deg = np.array([lon_deg])
        is_single = True

    assert lon_deg.ndim == 1
    assert lat_deg.ndim == 1
    assert lon_deg.shape[0] == lat_deg.shape[0]
    
    max_lon = 179.999    
    max_lat = 85.05
    
    lon_deg = np.clip(lon_deg, -max_lon, max_lon)
    lat_deg = np.clip(lat_deg, -max_lat, max_lat)    
    
    lon_rad = np.radians(lon_deg) 
    lat_rad = np.radians(lat_deg) 
    n = zoom_power(zoom)
    
    ## x_tile/y_tile are rounded down 255.99 -> 255
    xtile = np.floor((lon_rad + np.pi) / (2 * np.pi) * n)

    interm = lat_rad / 2 + np.pi/ 4
    ytile = np.floor((np.pi - np.log(np.tan(interm))) / (2 * np.pi) * n)

    if is_single == True:
        xtile: int = int(xtile[0])
        ytile: int = int(ytile[0])

    return (xtile, ytile)


def np_idx2deg(xtile: Union[np.ndarray, int], 
               ytile: Union[np.ndarray, int], 
               zoom: int,
               offset = 0.5) -> (Union[np.ndarray, int],Union[np.ndarray, int]):
    """Converts tile index back to lat/lon coordinates.

    Arguments:
        xtile - integer or numpy array of integers, tile 'x' coordinate 
        ytile - integer or numpy array of integers, tile 'y' coordinate
        zoom - integer, zoom level which was used for indexing tile.
        offset - which coordinate inside the tile to return: 
              -- If 0.5 - return center of the tile (recommended), 
              -- If 0 - return left upper corner, 
              -- If 1 - return bottom right corner
        
    Sources:
        -- https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """
    is_single = False # should we return array or single number
    if _check_if_float(xtile):
        xtile = np.array([xtile])
        is_single = True

    if _check_if_float(ytile):
        ytile = np.array([ytile])
        is_single = True

    assert xtile.ndim == 1
    assert ytile.ndim == 1
    assert xtile.shape[0] == ytile.shape[0]
    


    offset = np.clip(offset, 0, 1)
    n = zoom_power(zoom)

    # cliping any wrong values
    xtile = np.clip(xtile, 0, n - 1)
    ytile = np.clip(ytile, 0, n - 1)       
    
    # np.floor((lon_rad + np.pi) / (2 * np.pi) * n)

    lon_rad = (xtile + offset) * (2 * np.pi) / n - np.pi
    lon_deg = lon_rad / np.pi * 180
    
    # converting ytile coordinates
    interm = np.pi - (ytile + offset) * (2 * np.pi) / n 
    interm = np.arctan(np.exp(interm))
    lat_rad = 2 * (interm - np.pi / 4)
    lat_deg = lat_rad / np.pi * 180

    if is_single == True:
        lat_deg: float = lat_deg[0]
        lon_deg: float = lon_deg[0]

    return (lat_deg, lon_deg)


def np_haversin(lat_deg1: np.ndarray,
                lon_deg1: np.ndarray, 
                lat_deg2: np.ndarray,
                lon_deg2: np.ndarray, 
               ) -> np.ndarray:
    """Computes haversine distance between two ponts.
        
       Returns distance in meters
        
       Arguments:
       lon_deg1: array of floats, longitude of the first point
       lat_deg1: array of floats, latitude of the first point
       lon_deg2: array of floats, longitude of the second point
       lat_deg2: array of floats, latitude of the second point
       
       Sources:
       -- https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """   
    earth_radius = 6371000
    lon_rad1 = np.radians(lon_deg1) 
    lat_rad1 = np.radians(lat_deg1)
    lon_rad2 = np.radians(lon_deg2) 
    lat_rad2 = np.radians(lat_deg2)

    
    sin_rad = np.sin((lat_rad2 - lat_rad1) / 2)
    sin_lon = np.sin((lon_rad2-lon_rad1) / 2)
    
    interm = sin_rad * sin_rad + np.cos(lat_rad2) * np.cos(lat_rad1) * sin_lon * sin_lon
    
    dist = 2 * np.arcsin(np.power(interm,0.5))
    dist_meters = np.round(dist * earth_radius,1)
    return dist_meters


def tile_size_meters(lat: Union[None, float], 
                     lon: Union[None, float], 
                     zoom: int) -> Dict[str,float]:
    """Return size in meters of each tile.

    This is a proxy, because tile size will be different in different parts of the world.
    """    
    n = zoom_power(zoom)

    if lat is not None and lon is not None:
        idx_x, idx_y = np_deg2idx(lat, lon, zoom = zoom)
    else:
        idx_x = n // 2
        idx_y = n // 2
    
    arr_xtile = np.array([idx_x, idx_x+1, idx_x,   idx_x + 1])
    arr_ytile = np.array([idx_y, idx_y,   idx_y+1, idx_y + 1])


    lat_deg, lon_deg = np_idx2deg(arr_xtile, arr_ytile, zoom = zoom)
    

    lon1 = np.array([lon_deg[0],lon_deg[0],lon_deg[0]])
    lat1 = np.array([lat_deg[0],lat_deg[0],lat_deg[0]])
    lon2 = np.array([lon_deg[1], lon_deg[2], lon_deg[3]])
    lat2 = np.array([lat_deg[1], lat_deg[2], lat_deg[3]])

    dist_meters = np_haversin(lat1, lon1, lat2, lon2)
    
    dist = {'zoom': zoom,
            'x_tile_distance': dist_meters[0],
            'y_tile_distance': dist_meters[1],
            'diag_tile_distance': dist_meters[2],
            }
    return dist
