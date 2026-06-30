# ME4OH_summer_project
Foundation year summer project using data from [MapEval4OceanHeat](https://data.csiro.au/collection/csiro:60826)


# Set up
brew install ffmpeg

Python venv setup commands;
- pip install netCDF4
- pip install geopandas
- pip install tqdm
- pip install celluloid  # to make animations

# Data
[TBC what data and stored where to let code work]

# Usage
From within your virtual environment run the following commands to load and do initial preprocessing of the data ready for the notebooks:
- `python Data/load_ohc_l1_data.py`
- `python Data/load_sst_ofam3_data.py`