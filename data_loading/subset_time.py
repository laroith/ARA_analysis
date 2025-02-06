import xarray as xr

def get_common_time_range(ds1, ds2, time_var="time"):
    """
    Get the overlapping time period between two datasets.

    Args:
        ds1, ds2: xarray datasets.
        time_var: Name of the time dimension.

    Returns:
        dict: Start and end time for the common period.
    """
    time_min = max(ds1[time_var].min().values, ds2[time_var].min().values)
    time_max = min(ds1[time_var].max().values, ds2[time_var].max().values)

    return {"start_time": time_min, "end_time": time_max}

def subset_time(ds, time_var="time", time_bounds=None):
    """
    Subset an xarray dataset to a given time range.

    Args:
        ds (xarray.Dataset): Dataset to subset.
        time_var (str): Name of the time variable.
        time_bounds (dict): Dictionary with 'start_time' and 'end_time'.

    Returns:
        xarray.Dataset: The subset dataset.
    """
    if time_bounds is None:
        return ds  # No subsetting

    return ds.sel({time_var: slice(time_bounds["start_time"], time_bounds["end_time"])})

def main():
    # Load datasets
    ensemble_ds = xr.open_dataset("data/subset_ensemble.nc")
    reference_ds = xr.open_dataset("data/processed_reference.nc")

    # Get common time range
    common_time_bounds = get_common_time_range(ensemble_ds, reference_ds)
    print(f"Common time range: {common_time_bounds}")

    # Subset the ensemble dataset to match the reference dataset's time range
    ensemble_time_subset = subset_time(ensemble_ds, time_bounds=common_time_bounds)

    print(f"Subset ensemble dataset time range: {ensemble_time_subset.time.values}")

    # Save subset dataset
    ensemble_time_subset.to_netcdf("data/final_subset_ensemble.nc")

if __name__ == "__main__":
    main()
