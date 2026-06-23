import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable

# TODO: Combine into unified plotting function

COUNTRIES_URL = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
WORLD = gpd.read_file(COUNTRIES_URL).rename({"ADMIN": "name"}, axis="columns")
regions = ['Southern Europe', 'Northern Africa', 'Western Africa', 'Western Europe', 'Northern Europe', 'Central America', 'South America', 'Northern America', 'Caribbean']
NA = WORLD[WORLD['SUBREGION'].isin(regions)]


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
    fig, ax = plt.subplots(figsize=(15, 9))

    # Get world countries, and plot
    WORLD.plot(ax=ax, color='lightgray', edgecolor='gray', linewidth=0.75)  # Add countries

    # Create a shared normalization object
    norm = Normalize(vmin=min_ohc, vmax=max_ohc)
    cmap = plt.cm.plasma   # Define the colormap

    # Plot OHC map
    s = ax.scatter(data.Longitude, data.Latitude, c=data.OHC, s=1, cmap='plasma', norm=norm)  # Plot OHC observations
    
    cbar = fig.colorbar(s, ax=ax, cmap=cmap, norm=norm)
    cbar.set_label('OHC $(Jm^{−2})$')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    # ax.set_facecolor("lightblue")

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
    plt.savefig(f"images/ohc_{basin}_map_{title}.png")
    plt.show()
    plt.close()


def plot_sst_map(data, title, min_sst, max_sst, sensor_coords=None, basin=None, cmap='plasma'):
    """For a given subset of data, plot the SST map over the world or filtered to a specific ocean basin
    
    Args:
        data (df or df.groupby object): dataframe (or df.groupby object of a dataframe) containing columns for
            latitude, longitude and observed SST.
        title (str): title for the plot and name for saved figure.
        min_sst (float): minimum value across entire dataset (ensures uniform colourbar)
        min_sst (float): maximum value across entire dataset (ensures uniform colourbar)
        basin (str, optional): basin to plot for. Current options are None (which will plot over the whole world),
            or "NA" (which will filter to the NA basin). Other options to be added as needed, but for now will throw error.
    Returns:
        Plot of OHC map, saved figure.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    

    # Create a shared normalization object
    norm = Normalize(vmin=min_sst, vmax=max_sst)
    # cmap = plt.cm.plasma   # Define the colormap

    # Plot SST map
    s = ax.scatter(data.Longitude, data.Latitude, c=data.SST, s=1, cmap=cmap, norm=norm)

    cbar = fig.colorbar(s, ax=ax, cmap=cmap, norm=norm)
    cbar.set_label('SST ($\\degree$ C)')

    if sensor_coords is not None:
        ax.scatter(sensor_coords[0], sensor_coords[1], marker='.', c='k')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    # ax.set_facecolor("lightblue")

    # Get world countries, and plot
    if basin is not None:
        if basin == "NA":
            ax.set_xlim([-80, 0])
            ax.set_ylim([0, 60])
            NA.plot(ax=ax, color='lightgray', edgecolor='gray', linewidth=0.75)  # Add countries
        else:
            plt.close()
            return
    else:
        basin = "world"
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])
        WORLD.plot(ax=ax, color='lightgray', edgecolor='gray', linewidth=0.75)  # Add countries

    plt.title(title)
    # plt.savefig(f"images/sst_{basin}_map_{title}.png")
    plt.show()
    plt.close()


def plot_compare_NA_sst_recon_truth(recon_data, truth_data, diff_data=None,
                                    title=None, sensor_coords=None):
    """For a given subset of data, plot the SST map over the NA basin
    TODO - UPDATE DOC STRINGS
    Args:
        data (df or df.groupby object): dataframe (or df.groupby object of a dataframe) containing columns for
            latitude, longitude and observed SST.
        title (str, optional): title for the plot and name for saved figure.
    Returns:
        Plot of OHC map, saved figure.
    """
    if diff_data is not None:
        fig, ax = plt.subplots(1, 3, figsize=(18, 10))
    else:
        fig, ax = plt.subplots(1, 2, figsize=(15, 5))

    # Create a shared normalization object for SST plots
    min_sst = min([min(recon_data.SST), min(truth_data.SST)])
    max_sst = max([max(recon_data.SST), max(truth_data.SST)])
    norm = Normalize(vmin=min_sst, vmax=max_sst)
    cmap = 'plasma'

    # Reconstruction subfigure
    s = ax[0].scatter(recon_data.Longitude, recon_data.Latitude, c=recon_data.SST, s=1, cmap=cmap, norm=norm)
    ax[0].set_title('Reconstructed SST ($\\degree$C)')
    if sensor_coords is not None:
        ax[0].scatter(sensor_coords[0], sensor_coords[1], marker='.', c='k')
    if diff_data is not None:
        cax = make_axes_locatable(ax[0]).append_axes('right', size='5%', pad=0.1)
        cbar = fig.colorbar(s, cax=cax, cmap=cmap, norm=norm)

    # Truth subfigure
    s = ax[1].scatter(truth_data.Longitude, truth_data.Latitude, c=truth_data.SST, s=1, cmap=cmap, norm=norm)
    ax[1].set_title('True SST ($\\degree$C)')

    if diff_data is not None:
        cax = make_axes_locatable(ax[1]).append_axes('right', size='5%', pad=0.1)
        cbar = fig.colorbar(s, cax=cax, cmap=cmap, norm=norm)
    else:
        cbar = fig.colorbar(s, ax=ax, cmap=cmap, norm=norm)
        cbar.set_label('SST ($\\degree$C)')
    
    # Difference subfigure
    if diff_data is not None:
        norm_diff = Normalize(vmin=-5, vmax=5)
        cmap_diff = 'bwr'
        s = ax[2].scatter(diff_data.Longitude, diff_data.Latitude, c=diff_data.SST, s=1, cmap=cmap_diff, norm=norm_diff)
        ax[2].set_title('Difference ($\\degree$C)')
        cax = make_axes_locatable(ax[2]).append_axes('right', size='5%', pad=0.1)
        cbar = fig.colorbar(s, cax=cax, cmap=cmap, norm=norm)

    # Style
    for a in ax:
        a.set_xlabel('Longitude')
        a.set_ylabel('Latitude')
        # a.set_facecolor('lightblue')
        a.set_xlim([-80, 0])
        a.set_ylim([0, 60])
        NA.plot(ax=a, color='lightgray', edgecolor='gray', linewidth=0.75)  # Add countries

    if title is not None:
        fig.suptitle(title)
    # plt.savefig(f"images/sst_comparison_{basin}_map_{title}.png")
    plt.show()
    plt.close()
