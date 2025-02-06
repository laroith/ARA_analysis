import xarray as xr
import numpy as np

def get_reference_extent(ref_ds, lat_var="lat", lon_var="lon"):
    """
    Extract the latitude and longitude extent of the reference dataset.
    
    Args:
        ref_ds (xarray.Dataset): The reference dataset.
        lat_var (str): Latitude variable name.
        lon_var (str): Longitude variable name.

    Returns:
        dict: Bounding box with min/max latitude and longitude.
    """
    lat_min, lat_max = ref_ds[lat_var].min().values, ref_ds[lat_var].max().values
    lon_min, lon_max = ref_ds[lon_var].min().values, ref_ds[lon_var].max().values

    return {"lat_min": lat_min, "lat_max": lat_max, "lon_min": lon_min, "lon_max": lon_max}

def subset_dataset(ds, lat_var="latitude", lon_var="longitude", bounds=None):
    """
    Subset an xarray dataset to a given lat/lon bounding box.

    Args:
        ds (xarray.Dataset): Dataset to subset.
        lat_var (str): Name of the latitude variable.
        lon_var (str): Name of the longitude variable.
        bounds (dict, optional): Dictionary with 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
                                 If None, the dataset is not subset.

    Returns:
        xarray.Dataset: The subset dataset.
    """
    if bounds is None:
        return ds  # No subsetting

    # Create boolean masks for latitude and longitude
    lat_mask = (ds[lat_var] >= bounds["lat_min"]) & (ds[lat_var] <= bounds["lat_max"])
    lon_mask = (ds[lon_var] >= bounds["lon_min"]) & (ds[lon_var] <= bounds["lon_max"])

    # Apply mask and return subset dataset
    return ds.where(lat_mask & lon_mask, drop=True)

def main():
    # Load datasets
    ensemble_ds = xr.open_dataset("data/processed_ensemble.nc")
    reference_ds = xr.open_dataset("data/processed_reference.nc")

    # Get reference dataset extent
    ref_bounds = get_reference_extent(reference_ds)

    print(f"Reference dataset bounds: {ref_bounds}")

    # Subset the ensemble dataset to match the reference dataset
    ensemble_subset = subset_dataset(ensemble_ds, bounds=ref_bounds)

    print(f"Subset ensemble dataset dimensions: {ensemble_subset.dims}")

    # Save subset dataset
    ensemble_subset.to_netcdf("data/subset_ensemble.nc")

if __name__ == "__main__":
    main()
