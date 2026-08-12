"""noaa_data.py

Helper function for loading NOAA SST data

Functionality for processing into same format as ME4OH OFAM3 data files, run this script

Prerequisites: SST_data.mat should be downloaded from https://github.com/Jan-Williams/pyshred/blob/main/Data/SST_data.mat
    and stored in "Data/NOAA" folder in this repository.

"""
# Standard imports
import os  # noqa: I001

# Third-party imports
import numpy as np
import pandas as pd
from scipy.io import loadmat
from tqdm import tqdm

# Local imports
from Data.load_ohc_l1_data import crop_df_to_area

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


def process_sst_data(temps, dates, lats, longs, world_data=True):
    """Iterate through temps array to build DataFrames for each timestamp, of the lat, long and SST values.
    Preprocesses this to change the Longitude coordinates ready for geopandas plotting and to filter to the NA basin.

    Args:
        temps (array): array with shape (len(dates), 1, len(lats), len(longs)) containing all the SST measurements
        dates (array): array of length 1879 containing corresponding Datetimes for the data
        lats (array): array of length 600 containing the range of latitude values for the data
        longs (array): array of length 1440 containing the range of longitude values for the data
        world_data (bool, optional): whether to save world data. Defaults to True, saving world data.

    Returns:
        None
    """  # noqa: D205
    for k in tqdm(range(len(dates))):
        sst_array = []
        lat_array = []
        long_array = []
        for i in range(len(lats)):
            for j in range(len(longs)):
                sst_array.append(temps[k][0][i][j])
                lat_array.append(lats[i])
                long_array.append(longs[j])
        df = pd.DataFrame({
            "Latitude": lat_array,
            "Longitude": long_array,
            "SST": sst_array
        })

        # Remove land values - these have filler value of -32768 used
        land_indexes = df.index[df['SST'] == -32768].tolist()  
        df = df.loc[~df.index.isin(land_indexes)]

        # Convert longitude to -180 to 180 format, allows plotting against geopandas world maps
        df['Longitude'] = df['Longitude'].apply(lambda x: -(360-x) if x > 180 else x)

        # Save world file
        if world_data:
            directory = f"Data/{data_type}/world/"
            os.makedirs(directory, exist_ok=True)
            df.to_csv(f"{directory}/{dates[k]}.csv", index=False)

        # Filter to NA basin
        directory = f"Data/{data_type}/NA/"
        os.makedirs(directory, exist_ok=True)
        na_df = crop_df_to_area(df, "NA", "Date")
        na_file_name = f"{directory}/{dates[k]}.csv"
        na_df.to_csv(na_file_name, index=False)


if __name__ == "__main__":
    # Read file
    print("Loading file...")
    temps, lats, longs, dates = load_data()
    print(temps.shape)

    # Preprocess data
    print("Preprocessing data...")
    process_sst_data(temps, dates, lats, longs, data_type="NOAA", world_data=False)