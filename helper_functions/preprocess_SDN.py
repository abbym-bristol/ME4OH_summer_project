"""preprocess_SDN.py

Preprocess data to produce SDN "sequences"
"""
import numpy as np
import torch


class SDNDataset(torch.utils.data.Dataset):
    """TBC"""
    def __init__(self, X, Y):  # noqa: D107
        self.X = X
        self.Y = Y
        self.len = X.shape[0]
        
    def __getitem__(self, index):  # noqa: D105
        return self.X[index], self.Y[index]
    
    def __len__(self):  # noqa: D105
        return self.len


def create_sdn_datasets(data, sensor_locs, test_lags=None):
    """TBC"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    if test_lags is None:
        # Not matching test dataset to SHRED test dataset
        data_in = np.array([data[i, sensor_locs] for i in range(len(data))])
        data_in = torch.tensor(data_in, dtype=torch.float32).to(device)
        data_out = torch.tensor(data, dtype=torch.float32).to(device)

    else:
        # Want only to test on the end point for each lag so can directly compare SDN and SHRED performance
        data_in = np.array([data[i+test_lags, sensor_locs] for i in range(len(data)-test_lags)])
        data_in = torch.tensor(data_in, dtype=torch.float32).to(device)
        ### -1 to have output be at the same time as final sensor measurements
        data_out = torch.tensor(data[np.array(range(len(data)-test_lags)) + test_lags - 1], dtype=torch.float32).to(device)

    dataset = SDNDataset(data_in, data_out)

    return dataset