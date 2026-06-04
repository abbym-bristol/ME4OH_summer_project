import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

COUNTRIES_URL = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
WORLD = gpd.read_file(COUNTRIES_URL).rename({"ADMIN": "name"}, axis="columns")

def plot_ohc_map(data, title, min_ohc, max_ohc, basin=None):
    """For a given subset of data, plot the OHC map over the world or filtered to a specific ocean basin
    
    Args:
        data (df or df.groupby object): dataframe (or df.groupby object of a dataframe) containing columns for
            latitude, longitude and observed OHC.
        title (str): title for the plot and name for saved figure.
        min_ohc (float): minimum OHC value across entire dataset (ensures uniform colourbar)
        min_ohc (float): maximum OHC value across entire dataset (ensures uniform colourbar)
        basin (str, optional): basin to plot for. Current options are None (which will plot over the whole world),
            or "NA" (which will filter to the NA basin). Other options to be added as needed, but for now will throw error.
    Returns:
        Plot of OHC map, saved figure.
    """
    _, ax = plt.subplots(figsize=(15, 9))

    # Get world countries, and plot
    WORLD.plot(ax=ax, color='lightgray', edgecolor='gray', linewidth=0.75)  # Add countries

    # Create a shared normalization object
    norm = Normalize(vmin=min_ohc, vmax=max_ohc)
    cmap = plt.cm.plasma   # Define the colormap

    # Plot OHC map
    s = ax.scatter(data.Longitude, data.Latitude, c=data.OHC, s=1, cmap='plasma', norm=norm)  # Plot OHC observations
    
    cbar = plt.colorbar(s, ax=ax, cmap=cmap, norm=norm)
    cbar.set_label('OHC $(Jm^{−2})$')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_facecolor("lightblue")

    if basin is not None:
        if basin == "NA":
            ax.set_xlim([-80, 0])
            ax.set_ylim([0, 60])
        else:
            plt.close()
            return
    else:
        basin = "world"
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])

    plt.title(title)
    plt.show()
    plt.savefig(f"images/ohc_{basin}_map_{title}.png")
    plt.close()