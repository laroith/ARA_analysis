import xarray as xr
import os
import re
from glob import glob

def load_dataset(filepath, dataset_type="ensemble"):
    """
    Loads a NetCDF dataset using xarray.

    Args:
        filepath (str): Path to the NetCDF file.
        dataset_type (str): "ensemble", "SPARTACUS", or "INCA".

    Returns:
        tuple: (xarray.Dataset, lat_var, lon_var)
    """
    ds = xr.open_dataset(filepath, chunks={"time": 100})  # Chunking for large files

    # Define latitude and longitude variable names based on dataset type
    if dataset_type == "ensemble":
        lat_var, lon_var = "latitude", "longitude"
    elif dataset_type == "SPARTACUS":
        lat_var, lon_var = "lat", "lon"
    elif dataset_type == "INCA":
        lat_var, lon_var = "lat", "lon"
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")

    return ds, lat_var, lon_var

def parse_member_id(filepath):
    """
    Parse the two-digit ensemble member from filenames like:
        total_precipitation_20170101_00.nc
        total_precipitation_20170101_01.nc
    Returns the string member ID (e.g. "00", "01", ...)
    """
    basename = os.path.basename(filepath)
    match = re.search(r"_(\d{2})\.nc$", basename)
    if not match:
        raise ValueError(f"Could not parse member ID from filename: {filepath}")
    return match.group(1)


def parse_member_from_filename(filepath):
    """
    Extract the ensemble member index from the filename.
    Example format: total_precipitation_20170102_00.nc -> member '00'.
    Adjust regex if naming changes.
    """
    base = os.path.basename(filepath)
    match = re.search(r"_(\d{2})\.nc$", base)
    if match:
        return match.group(1)  # e.g. '00', '01'
    else:
        raise ValueError(f"Cannot parse ensemble member from file: {filepath}")

def unify_lat_lon(ds, lat_name="latitude", lon_name="longitude"):
    """
    Ensures ds can be concatenated whether lat/lon are 1D or 2D.
    - If 2D, rename to lat2d/lon2d and remove from ds.coords.
    - If 1D, leave as is.
    
    Args:
        ds (xarray.Dataset): The dataset to unify.
        lat_name (str): The variable name for latitude.
        lon_name (str): The variable name for longitude.
    
    Returns:
        xarray.Dataset: Modified dataset ready for concatenation.
    """
    # Check if 'lat_name' and 'lon_name' exist:
    if lat_name not in ds.variables or lon_name not in ds.variables:
        # If missing, no unification needed or you might raise an error
        return ds
    
    # If shape is (lat, lon), it's likely 2D
    if ds[lat_name].ndim == 2 and ds[lon_name].ndim == 2:
        # Rename them to avoid alignment issues
        ds = ds.rename({lat_name: "lat2d", lon_name: "lon2d"})
        # Remove them from coordinates if they’re listed there
        for coord in list(ds.coords):
            if coord in ["lat2d", "lon2d"]:
                ds = ds.set_coords(ds.coords.keys() - {coord})
    else:
        # Possibly 1D lat/lon -> Do nothing special
        pass
    
    return ds

def load_ensemble_files(file_pattern, chunks=None):
    """
    Loads multiple daily netCDF files for different ensemble members, 
    concatenates them along 'time', then merges them along a new 'member' dimension.

    Args:
        file_pattern (str): Glob pattern to find daily ensemble files 
                            e.g. 'data/20170102/total_precipitation_20170102_*.nc'
        chunks (dict, optional): Dictionary for Dask chunking 
                                 e.g. {'time': 24, 'lat': 100, 'lon': 100}

    Returns:
        xarray.Dataset: A dataset with dims (time, lat, lon, member).
    """
    filepaths = sorted(glob(file_pattern))
    if not filepaths:
        raise FileNotFoundError(f"No files found matching pattern: {file_pattern}")

    # Create a list for all opened Datasets
    ds_list = []

    for fp in filepaths:
        member_id = parse_member_from_filename(fp)

        # Lazy load with Dask
        ds = xr.open_dataset(fp, chunks=chunks)
        # Add 'member' dimension
        ds = ds.expand_dims({"member": [member_id]})

        ds_list.append(ds)

    # Combine all datasets along 'member' and 'time' coordinates
    # This will produce (time, lat, lon, member).
    ds_ensemble = xr.combine_by_coords(ds_list, combine_attrs="override")

    # Reorder dims if necessary (time, lat, lon, member)
    ds_ensemble = ds_ensemble.transpose("time", "lat", "lon", "member")

    return ds_ensemble

def load_ensemble_any_latlon(file_pattern, chunks=None):
    """
    Loads multiple daily netCDF files that may have either 1D or 2D lat/lon,
    groups them by ensemble member, concatenates along 'time' for each member,
    and finally concatenates across 'member'.
    
    Args:
        file_pattern (str): Glob pattern (e.g. "data/20170102/total_precipitation_*.nc")
        chunks (dict, optional): Dictionary for Dask chunking, e.g. {"time": 24, "lat": 200, "lon": 200}
        
    Returns:
        xarray.Dataset with dims (time, lat, lon, member) or (time, y, x, member),
        depending on your dimension names. If lat/lon are 2D, they become data vars `lat2d`, `lon2d`.
    """
    filepaths = sorted(glob(file_pattern))
    if not filepaths:
        raise FileNotFoundError(f"No files match pattern: {file_pattern}")

    # Group by ensemble member
    member_files = {}
    for fp in filepaths:
        member_id = parse_member_id(fp)
        member_files.setdefault(member_id, []).append(fp)

    member_datasets = []
    for m_id, fps in member_files.items():
        ds_list = []
        for f in sorted(fps):
            ds = xr.open_dataset(f, decode_coords="all", chunks=chunks)
            # Unify lat/lon so we can concat easily
            ds = unify_lat_lon(ds, lat_name="latitude", lon_name="longitude")
            ds_list.append(ds)
        
        # Concat along time with minimal coordinate alignment
        ds_time = xr.concat(ds_list, dim="time", coords="minimal", join="override")
        
        # Expand to add 'member' dimension
        ds_time = ds_time.expand_dims({"member": [m_id]})
        member_datasets.append(ds_time)

    # Final concat along 'member'
    ds_ensemble = xr.concat(member_datasets, dim="member", coords="minimal", join="override")
    
    # Reorder dims if needed: (time, lat, lon, member)
    # If your lat/lon dims are named differently, adjust here
    # Check for existence of dims before reordering
    if "member" in ds_ensemble.dims and "time" in ds_ensemble.dims:
        # For 1D lat/lon
        if "lat" in ds_ensemble.dims and "lon" in ds_ensemble.dims:
            ds_ensemble = ds_ensemble.transpose("time", "lat", "lon", "member", ...)
        # For 2D lat/lon (now called lat2d/lon2d)
        elif "lat" in ds_ensemble.dims and "lon" not in ds_ensemble.dims:
            # maybe your dimension is "lat" and "lon" was replaced by "lon2d"? No reordering needed.
            pass
        else:
            pass  # Skip reordering if dims are 2D

    return ds_ensemble

def main():
    # Example usage:
    # 1. Load single dataset (e.g., SPARTACUS)
    spartacus_ds = load_dataset(os.path.join("data", "SPARTACUS2-DAILY_RR_2016.nc"))
    print("SPARTACUS dataset loaded successfully.")
    print(spartacus_ds)

    # 2. Load multiple ensemble files
    pattern = os.path.join("data", "20170102", "total_precipitation_20170102_*.nc")
    ensemble_ds = load_ensemble_files(pattern, chunks={"time": 24, "lat": 200, "lon": 200})
    print("Ensemble dataset loaded successfully.")
    print(ensemble_ds)

if __name__ == "__main__":
    main()

