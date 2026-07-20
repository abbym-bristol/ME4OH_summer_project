"""preprocess_sst_ofam3_shred.py

Helper functions for preprocessing ME4OH data SST OFAM3 data for the SHRED algorithm

Prerequisites: load_sst_ofams3_data.py must be run first, producing NA basin data stored under NA_DATA_PATH

"""
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
    """Takes input sequence of sensor measurements with shape (batch size, lags, num_sensors)
    and corresponding measurements of high-dimensional state, return Torch dataset
    
    Origin: https://github.com/Jan-Williams/pyshred/blob/main/processdata.py
    """  # noqa: D205
    def __init__(self, X, Y):  # noqa: D107
        self.X = X
        self.Y = Y
        self.len = X.shape[0]
        
    def __getitem__(self, index):  # noqa: D105
        return self.X[index], self.Y[index]
    
    def __len__(self):  # noqa: D105
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

def load_files():
    """Load files and get data from files that have already been preprocessed to contain only
    North Atlantic basin data using load_sst_ofam3_data.py and stored in NA_DATA_PATH

    Returns:
        sst_data (2D numpy array): SST value at each time for each lat/long across area used
            2D array of format [[array of lat/long SST values for time 1], [array of lat/long SST values for time 2], ...]
        dates (numpy array): array of dates for each time in dataset (from filenames)
        lats (numpy array): array of latitudes corresponding to SST values
        longs (numpy array): array of longitudes corresponding to SST values
    """  # noqa: D205
    # TODO: alter so either saves out reformatted version or loads that if it exists?

    # Drop final file path -> not a full week out from penultimate path.
    file_paths = [f for f in sorted(glob(os.path.join(NA_DATA_PATH, "*.csv")))][:-1]

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


def split_ordered_data(data, dates, all_dates=False, train_frac=0.75):
    """Split ordered data into training, validation and test sets according to date

    Args:
        data (2D numpy array): 2D array of data to split of format [[values for time 1], [values for time 2], ...]
        dates (numpy array): array of dates for each time in data
        all_dates (bool, optional): whether to return all the date arrays, if False only test_dates is returned.
        train_frac (float, optional): fraction of training data to use, defaults to 0.75.

    Returns:
        train, val, test (2D numpy arrays): train, val and test splits of data using ratio train_frac:(1-train_frac)/2:(1-train_frac)/2
        train_dates, val_dates (numpy array, optional): arrays of dates for train and val sets; returned only if all_dates is True.
        test_dates (numpy array): array of dates for test set
    """
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

    if all_dates: 
        train_dates = dates[:n_train]
        val_dates = dates[n_train:n_train + n_val]
    test_dates = dates[n_train + n_val:]

    if len(test) != n_test:  # Sanity check
        raise ValueError("Test data of wrong length")

    if all_dates:
        return train, val, test, train_dates, val_dates, test_dates
    else:
        return train, val, test, test_dates


def create_shred_sequences(data, sensor_locs, lags=LAGS):
    """Create sequences for input to the SHRED model

    Args:
        data (2D numpy array): 2D array of data to split of format [[values for time 1], [values for time 2], ...]
        sensor_locs (list): indexes corresponding to the shape of the values for time t in data that indicate the sensor locations to use for the model
        lags (int, optional): number of weeks in each sequence, defaults to LAGS (52)

    Returns:
        dataset (TimeSeriesDataset): torch tensor dataset of input sequences and labels (entire data field at the end of each sequence)
    """
    num_sensors = len(sensor_locs)
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
