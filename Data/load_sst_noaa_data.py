"""noaa_data.py

Helper function for loading NOAA SST data

Functionality for processing into same format as ME4OH OFAM3 data files, run this script

Prerequisites: SST_data.mat should be downloaded from https://github.com/Jan-Williams/pyshred/blob/main/Data/SST_data.mat
    and stored in "Data/NOAA" folder in this repository.

"""
# Third-party imports
import numpy as np  # noqa: I001
import pandas as pd
from scipy.io import loadmat

# Local imports
from Data.load_sst_ofam3_data import process_sst_data

def load_data(data_path='Data/NOAA/SST_data.mat'):
    """Load NOAA SST data for Original SHRED comparisons

    Args:
        data_path (str): path to NOAA SST data

    Returns:
        data (numpy array): SST data
        lats (numpy array): array of latitudes corresponding to SST values
        longs (numpy array): array of longitudes corresponding to SST values
        dates (numpy array): array of dates corresponding to SST values (bodged by me bc original SHRED doesn't do this)
    """
    # Set up dates
    start_date = "1992-01-01"
    end_date = "2018-10-25"  # NOTE: these dates have been bodged by me to give 1400 weeks of data
    dates = pd.date_range(start=start_date, end=end_date, freq="W-THU").tolist()
    dates = np.array([d.date() for d in dates])

    # Set up coordinates
    lat_range = np.arange(89.5, -90.0, -1.0)   # 180 points, descending: 89.5 to -89.5
    long_range = np.arange(0.5, 360.0, 1.0)     # 360 points: 0.5 to 359.5

    # 2D meshgrid if for lat/lon paired at every grid cell
    lon2d, lat2d = np.meshgrid(long_range, lat_range)  # shape (180, 360) each
    longs = lon2d.reshape(-1)
    lats = lat2d.reshape(-1)

    # Convert longitude to -180 to 180 format, allows plotting against geopandas world maps
    longs = np.where(longs > 180, longs - 360, longs)  # <-- do this as separate step because dataset is defined for 0.5-359.5 and worry about order being muddled

    # Load data
    load_X = loadmat(data_path)['Z'].T
    mean_X = np.mean(load_X, axis=0)
    ocean_idx = np.where(mean_X != 0)[0]  # Make mask to remove land regions from the data

    # Keep only the coordinates that correspond to the ocean points
    longs = longs[ocean_idx]
    lats = lats[ocean_idx]

    # Keep the SST data aligned with those coordinates
    data = load_X[:, ocean_idx]

    return data, lats, longs, dates


if __name__ == "__main__":
    # Read file
    print("Loading file...")
    temps, dates, lats, longs = load_data()

    # Preprocess data
    print("Preprocessing data...")
    process_sst_data(temps, dates, lats, longs, data_type="NOAA", world_data=False)