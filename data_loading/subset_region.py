import xarray as xr
import numpy as np

def unify_lat_lon_names(ds, lat_name="lat", lon_name="lon"):
    """
    Ensures 'lat' and 'lon' exist in ds by renaming 
    any of ['latitude', 'Longitude', etc.] if present.
    
    Args:
        ds (xarray.Dataset): The dataset to unify.
        lat_name (str): Desired name for latitude variable (default 'lat').
        lon_name (str): Desired name for longitude variable (default 'lon').
        
    Returns:
        xarray.Dataset: Dataset with renamed lat/lon variables, if found.
        
    Example:
        ds = unify_lat_lon_names(ds)
        # => ds has ds["lat"] and ds["lon"] whether 
        #    it was "latitude"/"longitude" or "lat"/"lon" before.
    """
    # Potential existing names we want to unify
    possible_lat_names = ["lat", "latitude"]
    possible_lon_names = ["lon", "longitude"]

    rename_dict = {}
    # Check if any possible lat variable is actually in ds
    for candidate in possible_lat_names:
        if candidate in ds.variables or candidate in ds.coords:
            rename_dict[candidate] = lat_name
            break
    
    # Check if any possible lon variable is in ds
    for candidate in possible_lon_names:
        if candidate in ds.variables or candidate in ds.coords:
            rename_dict[candidate] = lon_name
            break

    # If rename_dict is empty, it means we didn't find lat or lon at all
    # but let's just rename what we can
    if rename_dict:
        ds = ds.rename(rename_dict)

    return ds


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

def subset_dataset(ds, lat_var="lat", lon_var="lon", bounds=None):
    """
    Subset an xarray dataset to a given lat/lon bounding box, 
    handling both 1D and 2D lat/lon variables.

    Args:
        ds (xarray.Dataset): Dataset to subset.
        lat_var (str): Name of the latitude variable (1D or 2D).
        lon_var (str): Name of the longitude variable (1D or 2D).
        bounds (dict, optional): Dictionary with 
                                 {'lat_min': ..., 'lat_max': ..., 
                                  'lon_min': ..., 'lon_max': ...}.
                                 If None, returns ds unmodified.
                                 
    Returns:
        xarray.Dataset: The subset dataset.

    Examples:
        >>> # 1D lat/lon
        >>> ds_sub = subset_dataset(ds, lat_var="lat", lon_var="lon", 
        ...                         bounds={"lat_min": 46, "lat_max": 49, 
        ...                                 "lon_min": 9, "lon_max": 17})
        
        >>> # 2D lat/lon
        >>> ds_sub = subset_dataset(ds, lat_var="lat2d", lon_var="lon2d", bounds=some_bounds)
    """
    if bounds is None:
        return ds  # No subsetting performed

    # 1) Retrieve latitude data
    if lat_var in ds.coords:
        lat_data = ds.coords[lat_var]
    elif lat_var in ds.variables:
        lat_data = ds[lat_var]
    else:
        raise KeyError(f"Dataset has no coordinate or variable named '{lat_var}'.")

    # 2) Retrieve longitude data
    if lon_var in ds.coords:
        lon_data = ds.coords[lon_var]
    elif lon_var in ds.variables:
        lon_data = ds[lon_var]
    else:
        raise KeyError(f"Dataset has no coordinate or variable named '{lon_var}'.")

    # Check if lat/lon are 1D or 2D
    if lat_data.ndim == 1 and lon_data.ndim == 1:
        # 1D bounding
        lat_mask = (lat_data >= bounds["lat_min"]) & (lat_data <= bounds["lat_max"])
        lon_mask = (lon_data >= bounds["lon_min"]) & (lon_data <= bounds["lon_max"])

        ds_sub = ds.sel({
            lat_var: lat_data[lat_mask],
            lon_var: lon_data[lon_mask]
        })

    else:
        # 2D bounding
        within_box = (
            (lat_data >= bounds["lat_min"]) & (lat_data <= bounds["lat_max"]) &
            (lon_data >= bounds["lon_min"]) & (lon_data <= bounds["lon_max"])
        )
        # Avoid boolean Dask array indexing error by computing the mask
        within_box = within_box.compute()
        ds_sub = ds.where(within_box, drop=True)

    return ds_sub



def subset_dataset_old(ds, lat_var="latitude", lon_var="longitude", bounds=None):
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
