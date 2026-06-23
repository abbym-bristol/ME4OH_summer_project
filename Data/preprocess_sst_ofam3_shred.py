"""preprocess_sst_ofam3_shred.py

Helper files for preprocessing ME4OH data SST OFAM3 data for SHRED algorithm

Prerequisites: load_sst_ofams3_data.py must be run first, giving NA basin data stored under NA_DATA_PATH

"""
# TODO - docstrings

import os
from glob import glob

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from Data.load_sst_ofam3_data import NA_DATA_PATH

NUM_SENSORS = 3
LAGS = 52  # The OFAM3 SST data is sampled weekly (unknown currently whether these are averaged or just for one day each week)
np.random.seed(42)


class TimeSeriesDataset(torch.utils.data.Dataset):
    '''Takes input sequence of sensor measurements with shape (batch size, lags, num_sensors)
    and corresponding measurements of high-dimensional state, return Torch dataset'''
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.len = X.shape[0]
        
    def __getitem__(self, index):
        return self.X[index], self.Y[index]
    
    def __len__(self):
        return self.len


# def load_reformat(data_path=NA_DATA_PATH):
#     # Load and reformat data
#     files = [f for f in glob(os.path.join(data_path, "*.csv"))]
#     reformat_data_path = os.path.join(data_path, "shred_format_data.csv")
#     if reformat_data_path in files:
#         print("Data already reformatted")

#     else:
#         print(f"Found {len(files)} files in {data_path} directory")
#         data, dates, lats, longs = load_files(files)

#         # Save out again for ease of processing
#         data.tofile(f'{data_path}/shred_format_data.csv', sep = ',')

def load_files(data_path=NA_DATA_PATH):
    # TODO: alter so either saves out reformatted version or loads that if it exists

    file_paths = [f for f in sorted(glob(os.path.join(data_path, "*.csv")))]

    sst_data = []
    dates = []
    
    for file_path in tqdm(file_paths, desc='Loading data'):
        df = pd.read_csv(file_path)
        if file_path == file_paths[0]:
            lats = df.Latitude.to_numpy()
            longs = df.Longitude.to_numpy()
        base_name = os.path.basename(file_path)
        date_str = os.path.splitext(base_name)[0]
        dates.append(pd.to_datetime(date_str).date())
        sst_data.append(df.SST.to_numpy())

    return np.array(sst_data), np.array(dates), lats, longs


def split_ordered_data(data, dates, train_frac=0.75):

    if len(data) != len(dates):  # Sanity check
        raise ValueError("data_frames and dates must have the same length")
    
    n_total = len(data)
    n_train = int(np.floor(n_total * train_frac))
    n_remaining = n_total - n_train
    n_val = n_remaining // 2
    n_test = n_remaining - n_val

    train = data[:n_train]
    val = data[n_train:n_train + n_val]
    test = data[n_train + n_val:]

    train_dates = dates[:n_train]
    val_dates = dates[n_train:n_train + n_val]
    test_dates = dates[n_train + n_val:]

    if len(test) != n_test:  # Sanity check
        raise ValueError("Test data of wrong length")

    return train, val, test, train_dates, val_dates, test_dates


def create_shred_sequences(data, sensor_locs, num_sensors=NUM_SENSORS, lags=LAGS):

    data_in = np.zeros((len(data) - lags, lags, num_sensors))
    for i in range(len(data_in)):
        data_in[i] = data[i:i+lags, sensor_locs]  # stores values between i and 52 weeks, at 3 sensor locations
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    data_in = torch.tensor(data_in, dtype=torch.float32).to(device)

    # +lags-1 to have output be at the same time as final sensor measurements
    data_out = torch.tensor(data[np.array(range(len(data)-lags)) + lags - 1], dtype=torch.float32).to(device)

    dataset = TimeSeriesDataset(data_in, data_out)

    return dataset


if __name__ == "__main__":
    # Load and reformat data
    data, dates, lats, longs = load_files()

    print("Preprocessing data...")
    train_data, val_data, test_data = split_ordered_data(data)

    # Normalise data
    sc = MinMaxScaler()
    sc = sc.fit(train_data)  # Computes min and max from training data only (prevent data leakage)
    train_transformed = sc.transform(train_data)  
    val_transformed = sc.transform(val_data)
    test_transformed = sc.transform(test_data)

    # Build sequences
    sensor_locations = np.random.choice(data.shape[1], size=NUM_SENSORS, replace=False)
    print(f"Sensor location indexes will be: {sensor_locations}")

    train_dataset = create_shred_sequences(train_transformed)
    val_dataset = create_shred_sequences(val_transformed)
    test_dataset = create_shred_sequences(test_transformed)
