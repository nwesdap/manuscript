import pandas as pd
import xarray as xr
import cartopy
import cartopy.crs as ccrs
from matplotlib import pyplot as plt
import matplotlib.path as mpath
import matplotlib.colors as colors
import cmocean

# Open NWESDAP
nwesdap = pd.read_parquet("data/NWESDAP_v20102026.parquet")

# Create dataframe with unique locations from NWESDAP
nwes_loca = nwesdap.drop_duplicates(
    subset=[
        "Longitude",
        "Latitude",
    ],
    keep="first",
)

# Open file containing location of 1000m isobath and NWESDAP boundaries
bathy1000 = pd.read_csv("data/bathy1000.csv", sep=",")

# Open GEBCO 2026 bathymetry
gebco = xr.open_dataset("data/gebco_2026_n75.0_s40.0_w-21.0_e25.0.nc")

# Extract variables from GEBCO
bathy_lon, bathy_lat, bathy_h = (
    gebco.elevation.lon,
    gebco.elevation.lat,
    gebco.elevation.values,
)
bathy_h[bathy_h > 0] = 0


## Projection settings
noProj = ccrs.PlateCarree()
myProj = ccrs.Robinson()
myProj._threshold = myProj._threshold / 20.0

## Make the figure
fig, ax = plt.subplots(
    figsize=(10, 7), dpi=600, subplot_kw={"projection": myProj}
)

# Map boundary
[ax_hdl] = ax.plot(
    [-17, 20, 20, -17, -17],
    [43, 43, 71, 71, 43],
    color="black",
    linewidth=0.5,
    marker="none",
    transform=noProj,
)

tx_path = ax_hdl._get_transformed_path()
path_in_data_coords, _ = tx_path.get_transformed_path_and_affine()

# Create a polygon
polygon = mpath.Path(path_in_data_coords.vertices)
ax.set_boundary(polygon)

# colorbar settings for bathymetry
divnorm = colors.TwoSlopeNorm(vmin=-5000.0, vcenter=-1000, vmax=0)
lightcmap = cmocean.tools.lighten(cmocean.cm.deep_r, 0.9)

# plot GEBCO bathymetry
im = ax.pcolormesh(
    bathy_lon,
    bathy_lat,
    bathy_h,
    transform=ccrs.PlateCarree(),
    cmap=lightcmap,
    norm=divnorm,
)

# Add colorbar on the map
cax = fig.add_axes([0.72, 0.16, 0.01, 0.27])

cbar = fig.colorbar(
    im,
    cax=cax,
    orientation="vertical",
    ticks=[-5000, -4000, -3000, -2000, -1000, -500, 0],
)
cbar.set_label("Bathymetry (m)", fontsize=10, color="black")
cbar.ax.tick_params(labelsize=10)
cbar.ax.yaxis.set_label_position("left")

cax.set_facecolor("white")
cax.patch.set_alpha(0.8)

# Add gridlines
ax.gridlines(
    draw_labels=True,
    x_inline=False,
    y_inline=False,
    linewidth=0.5,
    color="gray",
    alpha=0.5,
    linestyle="--",
)

# plot 1000m isobath and boundaries
ax.plot(
    bathy1000.lon,
    bathy1000.lat,
    c="k",
    transform=ccrs.PlateCarree(),
    zorder=8,
)

ax.coastlines(resolution="10m", linewidth=0.1)
feature = cartopy.feature.NaturalEarthFeature(
    name="coastline",
    category="physical",
    scale="50m",
    edgecolor="#4a4435",
    facecolor="#dcd5c1",
    zorder=9,
)
ax.add_feature(feature)

# plot NWESDAP datapoints location
ax.scatter(
    nwes_loca.Longitude,
    nwes_loca.Latitude,
    c="#fa0000",
    edgecolor="#7d0108",
    linewidth=0.5,
    marker="o",
    s=7,
    transform=ccrs.PlateCarree(),
    zorder=10,
)

# Add annotations
ax.annotate(
    "Fyn",
    xy=(10.5, 55.5),
    xytext=(10.5, 52),
    xycoords=ccrs.PlateCarree(),
    arrowprops=dict(
        color="#343538", shrink=0.05, width=1, headwidth=7, headlength=5
    ),
    color="#343538",
    horizontalalignment="center",
    verticalalignment="center",
    zorder=11,
)

ax.annotate(
    "Sjælland",
    xy=(12, 55.5),
    xytext=(14, 53),
    xycoords=ccrs.PlateCarree(),
    arrowprops=dict(
        color="#343538", shrink=0.05, width=1, headwidth=7, headlength=5
    ),
    color="#343538",
    horizontalalignment="center",
    verticalalignment="center",
    zorder=11,
)

ax.annotate(
    "Capbreton\ncanyon",
    xy=(-1.4, 43.6),
    xytext=(1, 45),
    xycoords=ccrs.PlateCarree(),
    arrowprops=dict(
        color="#343538", shrink=0.05, width=1, headwidth=7, headlength=5
    ),
    color="#343538",
    ha="left",
    horizontalalignment="center",
    verticalalignment="center",
    zorder=11,
)

fig.tight_layout()
plt.savefig("figures/Figure1.png", transparent=True, dpi=300)
