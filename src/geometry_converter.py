import numpy as np
import pandas as pd
from shapely.geometry.polygon import Polygon
from src import np_tiles_converter as tiles_converter
import geopandas as gpd

def _xy_combinations(x: np.ndarray, y: np.ndarray):
    """Fast cartesian product of two arrays.

    Given two arrays returns all combinations of their members.
    any x <-> any y
    """
    return np.dstack(np.meshgrid(x, y)).reshape(-1, 2)


def polygon_to_tiles(geo_polygon: Polygon) -> pd.DataFrame:
    """Returns all tiles lat/lon coords that are inside given polygon.

    """
    assert isinstance(geo_polygon, Polygon)

    # coordinates of the polygon boundary 
    # is is two dimensional array. Second dimension is equal to two
    # it should have shape = [:,2] and first column = lon, second = lat (!!)
    london_bound_coords = np.array(geo_polygon.exterior.coords)

    x_tiles_arr, y_tiles_arr = tiles_converter.np_deg2idx(london_bound_coords[:,1],london_bound_coords[:,0],zoom=19)

    # for linter
    x_tiles_arr: np.ndarray = x_tiles_arr
    y_tiles_arr: np.ndarray = y_tiles_arr

    # Now we create list of all candidate tiles that could be inside our Polygon 
    min_x, max_x = x_tiles_arr.min(), x_tiles_arr.max()
    min_y, max_y = y_tiles_arr.min(), y_tiles_arr.max()
    all_x = np.ogrid[min_x:max_x+1]
    all_y = np.ogrid[min_y:max_y+1]
    tiles_idx = _xy_combinations(all_x, all_y)

    # coordinates of tiles centers
    center_lats, center_lons = tiles_converter.np_idx2deg(tiles_idx[:,0],tiles_idx[:,1], zoom=19)

    # cleaning memory
    del  tiles_idx
    
    df_polygon = gpd.GeoDataFrame(data = {'geometry': [geo_polygon]})

    # all candidates who might be inside our Polygon boundaries
    candidate_pts = gpd.GeoSeries.from_xy(x = center_lons, y = center_lats)
    # candidate_pts.set_crs(crs=df_polygon.crs,inplace=True)
    candidate_pts.name = 'geometry'
    candidate_pts = candidate_pts.to_frame()
    n_candidates = candidate_pts.shape[0]

    
    # processing this lines will take quite a while
    print ("Checking which points are inside polygon boundary", flush = True)
    print (f"Count candidate points: {n_candidates}", flush = True)

    inner_pts = gpd.tools.sjoin(candidate_pts, 
                        df_polygon, 
                        predicate="within", 
                        how='inner')

    n_inner_pts = inner_pts.shape[0]
    print (f"Count points inside polygon: {n_inner_pts}", flush = True)

    df_coords = pd.DataFrame({"lat": inner_pts['geometry'].y.values, 
                              "lon": inner_pts['geometry'].x.values} )

    return df_coords