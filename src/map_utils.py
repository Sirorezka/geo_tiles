import folium
import numpy as np
from src import plot_utils
from folium.features import DivIcon


def add_points_to_map(
    map_obj: folium.Map,
    lat_arr: np.ndarray,
    lon_arr: np.ndarray,
    color: str = "blue",
    radius: float = 10,
):
    n_points = len(lon_arr)
    for i in range(n_points):
        folium.CircleMarker(
            location=[lat_arr[i], lon_arr[i]], radius=radius, color=color
        ).add_to(map_obj)

    return map_obj


def add_tile_to_map(
    tile_x_idx: int,
    tile_y_idx: int,
    zoom: int,
    map_obj: folium.Map,
    radius: float = 10,
    color: str = "blue",
    font_size: int = -1,
):
    """
    Plot single tile based on it's coordinates.

    """

    # Tile box coordinates
    tile_box_coord = plot_utils.get_tile_box_coords(tile_x_idx, tile_y_idx, zoom)

    # Plot tile box
    folium.PolyLine(tile_box_coord, color=color).add_to(map_obj)

    # Plot text in the center of tile box
    if font_size > 0:
        # tile center
        x_center_lat, y_center_lon = plot_utils.get_tile_center_coords(
            tile_x_idx, tile_y_idx, zoom
        )

        # Add text to tile
        folium.map.Marker(
            [x_center_lat, y_center_lon],
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(20, 20),
                html=f"<div style='font-size: {font_size}pt'>[{tile_x_idx},<br> {tile_y_idx}]</div>",
            ),
        ).add_to(map_obj)

    return map_obj


def add_box_to_map(
    map_obj: folium.Map,
    lon_arr: np.ndarray,
    lat_arr: np.ndarray,
    radius: float = 10,
    color: str = "blue",
):
    n_points = len(lon_arr)
    locations = [[lat_arr[i], lon_arr[i]] for i in range(n_points)]

    folium.PolyLine(locations=locations, radius=radius, color=color).add_to(map_obj)

    return map_obj
