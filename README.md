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


### 3. Perform Spatial & Temporal Subsetting
Region Selection & Spatial Subsetting:

python data_loading/subset_region.py


Time Selection & Temporal Alignment:

python data_loading/subset_time.py


### 4. Run Tests in Jupyter Notebook
For interactive debugging and testing:

jupyter-notebook

Open notebooks/spatial_alignment_test.ipynb




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
