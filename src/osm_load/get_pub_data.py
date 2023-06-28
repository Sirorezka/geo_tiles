import osmnx as ox
import geopandas as gpd


def get_london_pubs():
    # Get place boundary related to the place name as a geodataframe
    tags = {"amenity": "pub"}

    pubs = ox.geometries_from_place("London", tags)
    pubs = pubs[["name", "geometry", "nodes", "ways"]]
    pubs.reset_index(inplace=True, drop=False)

    x_arr = []
    y_arr = []
    for i, row in pubs.iterrows():
        if hasattr(row.geometry, "x"):
            # if node
            x = row.geometry.x
            y = row.geometry.y
        elif hasattr(row.geometry, "exterior"):
            # if single area
            x, y = np.array(row.geometry.exterior.coords).mean(axis=0)
        else:
            # if multipolygon (several areas)
            x = np.mean(row.geometry.centroid.xy[0])
            y = np.mean(row.geometry.centroid.xy[1])

        x_arr.append(x)
        y_arr.append(y)

    df_pubs = pd.DataFrame({"pub_name": pubs["name"], "lon": x_arr, "lat": y_arr})
    return df_pubs
