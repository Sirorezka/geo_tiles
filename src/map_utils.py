import folium
import numpy as np


def add_points_to_map(map_obj: folium.Map,                      
                      lat_arr: np.ndarray,
                      lon_arr: np.ndarray,                                  
                      color: str = "blue",
                      radius: float = 10):
    
    n_points = len(lon_arr)
    for i in range(n_points):
        folium.CircleMarker(location = [lat_arr[i],
                             lon_arr[i]],
                             radius = radius,
                             color = color).add_to(map_obj)
        
    return map_obj


def add_box_to_map(map_obj: folium.Map,
                   lon_arr: np.ndarray, 
                   lat_arr: np.ndarray,
                   radius: float = 10,
                   color: str = "blue"):
    
    n_points = len(lon_arr)
    locations = [[lat_arr[i], lon_arr[i]] for i in range(n_points)]
    
    folium.PolyLine(locations = locations,
                        radius = radius, 
                        color = color).add_to(map_obj)
        
    return map_obj