# 🌍 Climate Data Analysis Project

## 📌 Overview
This project processes and analyzes ensemble climate datasets, ensuring **spatial and temporal alignment** with reference datasets (**SPARTACUS** and **INCAL**). The project is modular and scalable, allowing for **custom region selection, ensemble analysis, and statistical processing**.

## 🛠️ Setup Instructions

### 1. Install Python & Dependencies
Ensure Python is installed, then install the required packages:

conda install -r requirements.txt


### 2. Load and inspect Data
To load and preview datasets, run:

python data_loading/load_data.py

We introduced a new function `load_ensemble_any_latlon()` (in `data_loading/load_data.py`) that:
1. **Discovers NetCDF files** via a glob pattern (e.g., `total_precipitation_2017010*.nc`).
2. **Parses ensemble member IDs** from filenames (e.g., `_00.nc`, `_01.nc`, etc.).
3. **Unifies lat/lon** by detecting if they are 1D or 2D.  
   - **2D** lat/lon arrays are renamed to `lat2d`, `lon2d` and removed from the coordinate system to avoid xarray alignment issues.
   - **1D** lat/lon arrays remain as coordinate variables.
4. **Concatenates** all daily files for each member along the `time` dimension.
5. **Combines** members along a new `"member"` dimension.  
6. **Utilizes Dask** for lazy loading and chunking to handle large datasets.

**Result:** A single `xarray.Dataset` with dimensions `(time, lat, lon, member)` (or `(time, lat2d, lon2d, member)` if 2D lat/lon). This standardizes multi-member ensembles, allowing for streamlined subsetting and aggregation.

### 3. Perform Spatial & Temporal Subsetting
Region Selection & Spatial Subsetting:

python data_loading/subset_region.py


Time Selection & Temporal Alignment:

python data_loading/subset_time.py


### 4. Temporal Aggregation with Ensemble Mean
The existing temporal aggregation functions in `utils/temporal_stats.py` (e.g., `aggregate_to_daily`) now have a `compute_ens_mean` argument:
- **`compute_ens_mean=True`** computes the ensemble mean across the `"member"` dimension before resampling.  
- **`compute_ens_mean=False`** keeps each ensemble member separate.


### 5. Run Tests in Jupyter Notebook
For interactive debugging and testing:

jupyter-notebook

Open notebooks/spatial_alignment_test.ipynb

In the `notebooks` folder, you can find the demonstration notebook (e.g., `test_ensemble_load.ipynb`) showing:
1. Loading multiple daily ensemble files with `load_ensemble_any_latlon()`.
2. Aggregating to daily sums (`aggregate_to_daily`) with `compute_ens_mean=True`.
3. Printing and plotting results to confirm correct functionality.


### 4. Next Steps
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
