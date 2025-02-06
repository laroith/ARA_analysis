import xarray as xr
import os

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

def main():
    # Define file paths
    ensemble_path = os.path.join("data", "ensemble_subset.nc")
    spartacus_path = os.path.join("data", "SPARTACUS2-DAILY_RR_2016.nc")
    incal_path = os.path.join("data", "INCAL_HOURLY_RR_201610.nc")

    # Load datasets
    ensemble_ds, ensemble_lat, ensemble_lon = load_dataset(ensemble_path, "ensemble")
    spartacus_ds, spartacus_lat, spartacus_lon = load_dataset(spartacus_path, "SPARTACUS")
    inca_ds, inca_lat, inca_lon = load_dataset(inca_path, "INCA")

    print("Ensemble Dataset:", ensemble_ds)
    print("SPARTACUS Dataset:", spartacus_ds)
    print("INCA Dataset:", inca_ds)

if __name__ == "__main__":
    main()
