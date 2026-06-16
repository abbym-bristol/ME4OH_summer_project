"""preporcess_sst_ofam3_shred.py

Preprocess ME4OH data SST OFAM3 data for SHRED algorithm

Prerequisites: load_sst_ofams3_data.py must be run first, giving NA basin data stored under NA_DATA_PATH

"""

import os
from glob import glob

import numpy as np
import pandas as pd
from tqdm import tqdm

from load_sst_ofam3_data import NA_DATA_PATH

NUM_SENSORS = 3
LAGS = 52  # The OFAM3 SST data is sampled weekly (unknown currently whether these are averaged or just for one day each week)
np.random.seed(42)

def pick_sensor_locations(first_file):
    df = pd.read_csv(first_file)
    sensor_locations = np.random.choice(len(df), size=NUM_SENSORS, replace=False)
    print(f"Sensor location indexes will be: {sensor_locations}")
    return sensor_locations


def load_files(file_paths):
    sst_data = []
    dates = []
    
    for file_path in tqdm(file_paths, desc='Loading data'):
        df = pd.read_csv(file_path)
        if file_path == file_paths[0]:
            lats = df.Latitude.tolist()
            longs = df.Longitude.tolist()
        base_name = os.path.basename(file_path)
        date_str = os.path.splitext(base_name)[0]
        dates.append(pd.to_datetime(date_str))
        sst_data.append(df.SST.tolist())
    return sst_data, dates, lats, longs


def split_ordered_data(data, train_frac=0.75):

    n_total = len(data)
    n_train = int(np.floor(n_total * train_frac))
    n_remaining = n_total - n_train
    n_val = n_remaining // 2
    n_test = n_remaining - n_val

    train = data[:n_train]
    val = data[n_train:n_train + n_val]
    test = data[n_train + n_val:]

    if len(test) != n_test:  # Sanity check
        raise ValueError("Test data of wrong length")

    return train, val, test

# Steps:
# 1. split dataset into training, test, etc
# 2. Convert to array shape instead
# 2. normalise according to entire training set (bc will use all data)
# 3. build sequences for input + labels for NUM_SENSORS
# 4. store somewhere so can read again quickly



# TODO: store dates in arrayas build preprocessed data array so can correspond these later
# TODO: add arguments to this file so can alter sensor numbers?

if __name__ == "__main__":
    # Build SHRED dataset
    files = [f for f in glob(os.path.join(NA_DATA_PATH, "*.csv"))]
    print(f"Found {len(files)} files in {NA_DATA_PATH} directory")

    sensor_locs = pick_sensor_locations(files[0])

    data, dates, lats, longs = load_files(files)
    if len(data) != len(dates):  # Sanity check
        raise ValueError("data_frames and dates must have the same length")
    train_data, val_data, test_data = split_ordered_data(data)
    

    



