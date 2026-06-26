"""load_ohc_l1_data.py

Load and preprocess ME4OH data for experimentation.

Caveats:
- Only using layer 1 of OHC data for initial work
"""

import datetime
import os
from glob import glob

import netCDF4 as nc
import numpy as np
import pandas as pd
from tqdm import tqdm

from Data.load_sst_en411_data import crop_df_to_area

DATA_PATH = 'Data/ME4OH_EN411_OFAM3/data/en4.1.1/1993-2014/'

def load_and_filter_ohc(filepath):
    """Load data file, extract variables, filter for layer 1 OHC"""
    file_data = nc.Dataset(filepath,'r')

    # Extract variables
    lat = file_data["ts_lat"][:].data  # Latitude
    long = file_data["ts_lon"][:].data  # Longitude
    time = file_data["en4_ymd"][:].data  # Year , month , day
    mask = file_data["dohc_mask_by_en4_maxdepth"][:].data # Valid profile mask
    dohc1 = file_data["dohc"][:, 0].data  # Layer 1 OHC anomaly target (NOTE: index 0 in python, index 1 in R)
    ssh = file_data["eta_t"][:].data  # Sea surface height
    wmo_inst_type = file_data["en4_wmo_inst_type"][:].data
    proj_name = file_data["en4_project_name"][:].data
    plat_num = file_data["en4_platform_number"][:].data

    # Close the file!
    file_data.close()

    # Filter to valid OHC
    # Only valid Layer-1 profiles included according to mask and remove NaNs
    idx = [i for i in range(len(mask)) if mask[i, 0] == 1]
    filtered_dohc1 = np.array([dohc1[i] for i in idx])
    filtered_lat = np.array([lat[i] for i in idx])
    filtered_long = np.array([long[i] for i in idx])
    filtered_date = np.array([datetime.date(int(time[i, 0]), int(time[i, 1]), int(time[i, 2])) for i in idx])
    filtered_ssh = np.array([ssh[i] for i in idx])
    filtered_wmo = np.array([''.join(list(map(lambda x: x.decode('utf-8'), wmo_inst_type[i]))).strip() for i in idx])
    filtered_proj_name = np.array([''.join(list(map(lambda x: x.decode('utf-8'), proj_name[i]))).strip() for i in idx])
    filtered_plat_num = np.array([''.join(list(map(lambda x: x.decode('utf-8'), plat_num[i]))).strip() for i in idx])

    # Make df
    ohc_df = pd.DataFrame({
        "Date": filtered_date,
        "Latitude": filtered_lat,
        "Longitude": filtered_long,
        "OHC": filtered_dohc1,
        "SSH": filtered_ssh,
        "WMO Instrument Type": filtered_wmo,
        "Project name": filtered_proj_name,
        "Platform number": filtered_plat_num
    })
    ohc_df = ohc_df.dropna()
    
    return ohc_df

if __name__ == "__main__":
    files = [f for f in glob(os.path.join(DATA_PATH, "*.nc"))]
    print(f"Found {len(files)} files in {DATA_PATH} directory")
    
    # Read all files
    print("Loading files...")
    ohc_df = load_and_filter_ohc(files[0])
    for path in tqdm(files[1:]):
        ohc_df = pd.concat([ohc_df, load_and_filter_ohc(path)])
        ohc_df['Date'] = pd.to_datetime(ohc_df['Date'])

    # Convert longitude to -180 to 180 format, allows plotting against geopandas world maps
    print("Converting longitudes...")
    tqdm.pandas()
    ohc_df['Longitude'] = ohc_df['Longitude'].progress_apply(lambda x: -(360-x) if x > 180 else x)
    world_file_name = "Data/ME4OH_EN411_OFAM3/OHC_WORLD_1993_2014.csv"
    ohc_df.to_csv(world_file_name, index=False)
    print(f"Whole dataset saved as {world_file_name}")

    # Filter to NA basin
    print("Filtering NA basin...")
    na_df = crop_df_to_area(ohc_df, "NA", "Date")
    na_file_name = "Data/ME4OH_EN411_OFAM3/OHC_NA_1993_2014.csv"
    na_df.to_csv(na_file_name, index=False)
    print(f"NA basin dataset saved as {na_file_name}")
