import xarray as xr
import numpy as np

def force_match_dimensions(ds_ref, ds_ens, ref_dims=("y", "x"), ens_dims=("lat", "lon")):
    """
    Force the reference dataset dims to match ensemble dims
    by renaming dimension coordinates only if shapes align.
    
    This is a quick approach that avoids broadcasting but only works
    if the data truly share the same shape. Otherwise, it can cause 
    silent misalignment or xarray errors.
    
    Args:
        ds_ref (xarray.Dataset or xarray.DataArray): The reference dataset.
        ds_ens (xarray.Dataset or xarray.DataArray): The ensemble dataset with dims (lat, lon).
        ref_dims (tuple): The dimension names in ds_ref to rename to (lat, lon).
        ens_dims (tuple): The dimension names in ds_ens, typically ("lat", "lon").
        
    Returns:
        (ds_ref_new, ds_ens): Two datasets with consistent dimension names if shapes match.
    """
    # for reference, we expect something like y=329, x=584
    y_dim, x_dim = ref_dims
    lat_dim, lon_dim = ens_dims
    
    # Step 1: Check if shapes match
    if (y_dim in ds_ref.dims) and (x_dim in ds_ref.dims):
        shape_ref = (ds_ref.dims[y_dim], ds_ref.dims[x_dim])
    else:
        raise ValueError(f"Reference dataset missing dims {ref_dims}")
    
    if (lat_dim in ds_ens.dims) and (lon_dim in ds_ens.dims):
        shape_ens = (ds_ens.dims[lat_dim], ds_ens.dims[lon_dim])
    else:
        raise ValueError(f"Ensemble dataset missing dims {ens_dims}")

    if shape_ref != shape_ens:
        raise ValueError(
            f"Dimension shapes do not match! ref={shape_ref}, ens={shape_ens}. "
            "You may need to regrid properly."
        )
    
    # Step 2: Rename reference dims y->lat, x->lon
    ds_ref_new = ds_ref.rename({y_dim: lat_dim, x_dim: lon_dim})
    
    # Optional: remove lat/lon coordinate arrays if they're not matching exactly
    # e.g., if lat(y, x) is 2D but we only want to keep the dimension lat in 1D
    # (In your use case, you might skip this or rename them to lat2d, lon2d)
    
    return ds_ref_new, ds_ens


#import ESMF
#import xesmf as xe

def regrid_to_ensemble(ds_ref, ds_ens, var_ref="RR"):
    """
    Reprojects ds_ref to ds_ens's lat-lon grid using xESMF.
    
    Args:
        ds_ref (xarray.Dataset or xarray.DataArray): Input on e.g. Lambert grid.
        ds_ens (xarray.Dataset or xarray.DataArray): Target grid in lat-lon.
        var_ref (str): Variable name in ds_ref to regrid.
        
    Returns:
        xarray.DataArray or xarray.Dataset: ds_ref regridded to ds_ens's grid.
    """
    # ds_ens must have coords named lat, lon
    # ds_ref might have lat(y, x), lon(y, x)
    
    # 1. Prepare the source grid
    ds_ref_grid = ds_ref.copy()
    ds_ref_grid = ds_ref_grid.rename({"lat": "src_lat", "lon": "src_lon"})  # if 2D
    # xESMF expects exactly "lat" and "lon" for the source or we pass them as coords
    
    # 2. Prepare the target grid
    ds_ens_grid = ds_ens.copy()
    # xESMF expects the coords to be named "lat", "lon" in the target as well
    
    # 3. Build regridder
    regridder = xe.Regridder(ds_ref_grid, ds_ens_grid, method="bilinear", reuse_weights=False)
    
    # 4. Regrid the reference variable
    ref_regridded = regridder(ds_ref_grid[var_ref])
    
    # Optionally restore the name or attach new coords
    ref_regridded.name = f"{var_ref}_on_ens_grid"
    
    return ref_regridded
