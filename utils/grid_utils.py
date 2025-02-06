import numpy as np
import xarray as xr

def get_spatial_bounds(ds, lat_var, lon_var):
    """
    Extracts latitude and longitude bounds from an xarray dataset.

    Args:
        ds (xarray.Dataset): The dataset.
        lat_var (str): Name of the latitude variable.
        lon_var (str): Name of the longitude variable.

    Returns:
        dict: A dictionary containing min/max latitude and longitude.
    """
    return {
        "lat_min": ds[lat_var].min().values,
        "lat_max": ds[lat_var].max().values,
        "lon_min": ds[lon_var].min().values,
        "lon_max": ds[lon_var].max().values
    }

def check_grid_alignment(ds1, ds2, lat_var1="latitude", lon_var1="longitude", lat_var2="lat", lon_var2="lon"):
    """
    Check if the latitude/longitude grids of two datasets overlap.

    Args:
        ds1 (xarray.Dataset): First dataset (e.g., ensemble).
        ds2 (xarray.Dataset): Second dataset (e.g., reference).
        lat_var1 (str): Latitude variable in ds1.
        lon_var1 (str): Longitude variable in ds1.
        lat_var2 (str): Latitude variable in ds2.
        lon_var2 (str): Longitude variable in ds2.

    Returns:
        bool: True if the grids overlap, False otherwise.
    """
    bounds1 = get_spatial_bounds(ds1, lat_var1, lon_var1)
    bounds2 = get_spatial_bounds(ds2, lat_var2, lon_var2)

    # Print bounds for debugging
    print(f"Dataset 1 (ensemble) bounds: {bounds1}")
    print(f"Dataset 2 (reference) bounds: {bounds2}")

    lat_overlap = (bounds1["lat_min"] <= bounds2["lat_max"]) and (bounds1["lat_max"] >= bounds2["lat_min"])
    lon_overlap = (bounds1["lon_min"] <= bounds2["lon_max"]) and (bounds1["lon_max"] >= bounds2["lon_min"])

    print(f"Latitude overlap: {lat_overlap}, Longitude overlap: {lon_overlap}")

    return lat_overlap and lon_overlap
