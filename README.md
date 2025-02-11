# 🌍 Climate Data Analysis Project

## 📌 Overview
This project processes and analyzes **ensemble climate datasets**, ensuring **spatial and temporal alignment** with reference datasets (**SPARTACUS** and **INCAL**). It is built with **modularity and scalability** in mind, enabling:

1. **Custom region selection** (subsetting both 1D and 2D lat/lon grids)  
2. **Ensemble handling** (load multiple members or compute ensemble means)  
3. **Temporal aggregation** (daily, monthly, annual)  
4. **Basic bias metrics** (Mean Error, Mean Absolute Error, RMSE)

---

## 🛠️ Setup Instructions

### 1. Install Python & Dependencies
Ensure Python is installed, then install the required packages:

conda install -r requirements.txt


### 2. Load and inspect Data
To load and preview datasets, run:

python data_loading/load_data.py

Ensemble Loading via load_ensemble_any_latlon()

Defined in data_loading/load_data.py. It:

    Discovers multiple NetCDF files using a glob pattern (e.g., total_precipitation_2017010*.nc).
    Parses ensemble member IDs from filenames (e.g., _00.nc or _01.nc).
    Unifies lat/lon to handle 2D lat/lon arrays (renamed to lat2d, lon2d) or keep 1D lat/lon.
    Concatenates all daily files along the time dimension, then merges along a new "member" dimension.
    Uses Dask for lazy loading and chunking.

Result: A single xarray.Dataset with dimensions (time, lat, lon, member) or (time, lat2d, lon2d, member).

### 3. Perform Spatial & Temporal Subsetting
Region Selection & Spatial Subsetting:

python data_loading/subset_region.py

Subsets to bounding boxes, handling 2D lat/lon with Dask by converting boolean masks to NumPy arrays before .where().
Works after unifying variable names (e.g., renaming latitude → lat).


Time Selection & Temporal Alignment:

python data_loading/subset_time.py

Ensures datasets share the same time range, slicing by start/end dates or the common overlap.

### 4. Temporal Aggregation with Ensemble Mean
The existing temporal aggregation functions in `utils/temporal_stats.py` (e.g., `aggregate_to_daily`) now have a `compute_ens_mean` argument:
- **`compute_ens_mean=True`** computes the ensemble mean across the `"member"` dimension before resampling.  
- **`compute_ens_mean=False`** keeps each ensemble member separate.

### 5. Basic Bias Metrics

Added in utils/bias_metrics.py:

    Mean Error (ME)
    Mean Absolute Error (MAE)
    Root Mean Squared Error (RMSE)

from utils.bias_metrics import compute_all_bias_metrics

metrics_ds = compute_all_bias_metrics(ds_ensemble["precipitation"],
                                      ds_reference["RR"],
                                      dim=["time", "lat", "lon"])
print(metrics_ds)


### 6. Run Tests in Jupyter Notebook
For interactive debugging and testing:

jupyter-notebook

Open notebooks/spatial_alignment_test.ipynb

In the `notebooks` folder, you can find the demonstration notebook (e.g., `test_ensemble_load.ipynb`) showing:
1. Loading multiple daily ensemble files with `load_ensemble_any_latlon()`.
2. Aggregating to daily sums (`aggregate_to_daily`) with `compute_ens_mean=True`.
3. Printing and plotting results to confirm correct functionality.


### 7. Next Steps
- **Further Statistical Analysis**: We can now easily compute bias metrics, e.g., Mean Error or RMSE, by comparing the ensemble dataset to single-member references (SPARTACUS, INCAL).  
- **Memory Performance**: Because we use Dask, operations on large multi-year datasets remain feasible without loading all data into memory at once.  
- **Customization**: The `unify_lat_lon()` function and `load_ensemble_any_latlon()` can be adapted for different naming conventions or additional ensemble metadata.


### Project Structure

├── data/                      # NetCDF climate datasets
│   ├── INCAL_HOURLY_RR_201611.nc
│   ├── SPARTACUS2-DAILY_RR_2016.nc
│   ├── testdata_prec_201611_short.nc
│   ├── test_subset_ensemble.nc
├── data_loading/              # Data processing modules
│   ├── check_quality.py       # Handles missing values and outliers
│   ├── load_data.py           # Loads NetCDF datasets
│   ├── preprocess.py          # General preprocessing utilities
│   ├── subset_region.py       # Spatial subsetting
│   ├── subset_time.py         # Temporal alignment
│   ├── __pycache__/           # Compiled Python cache (ignored)
├── utils/                     # Utility scripts
│   ├── grid_utils.py          # Grid alignment functions
│   ├── temporal_stats.py      # Aggregation & grouping (daily, monthly, etc.)
│   ├── bias_metrics.py        # Mean Error, MAE, RMSE
├── notebooks/                 # Jupyter notebooks for testing
│   ├── spatial_alignment_test.ipynb
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── .gitignore                 # Files to ignore in Git




### 👨‍💻 Contributing

1. Clone the repository:

git clone <repository-url>

2. Create a new branch for your feature:

git checkout -b feature-xyz

3. Commit your changes:

git add .
git commit -m "Added feature XYZ"
git push origin feature-xyz

4. Open a Pull Request on GitHub.
