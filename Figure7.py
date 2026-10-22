import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import cartopy
import cartopy.crs as ccrs
import matplotlib.path as mpath
import cartopy.feature as cfeature

# Import dataset
nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")
nwes = nwes.replace([-999, "-999"], np.nan)

spring = nwes.query("Month_UTC > 2 and Month_UTC < 6 ")
summer = nwes.query("Month_UTC> 5 and Month_UTC < 9 ")
autumn = nwes.query("Month_UTC > 8 and Month_UTC < 12 ")
winter = nwes.query("not(Month_UTC > 2 and Month_UTC < 12) ")


# %%

# Define the seasons with their grid positions and panel labels
seasons = {
    "Spring": (spring, 0, 0, "(a)"),
    "Summer": (summer, 0, 1, "(b)"),
    "Autumn": (autumn, 1, 0, "(c)"),
    "Winter": (winter, 1, 1, "(d)"),
}

noProj = ccrs.PlateCarree()
myProj = ccrs.Robinson()
myProj._threshold = myProj._threshold / 20.0

fig, axes = plt.subplots(
    nrows=2,
    ncols=2,
    figsize=(12, 10),
    dpi=300,
    subplot_kw={"projection": myProj},
)

for name, (season, row, col, label) in seasons.items():
    ax = axes[row, col]

    # Define custom region boundary
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

    polygon = mpath.Path(path_in_data_coords.vertices)
    ax.set_boundary(polygon)  # Masks out unwanted parts

    ax.add_feature(cfeature.OCEAN, facecolor="white")

    # Gridlines setup
    gl = ax.gridlines(
        draw_labels=True,
        crs=ccrs.PlateCarree(),
        x_inline=False,
        y_inline=False,
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False

    ax.coastlines(resolution="10m", linewidth=0.1)

    feature = cartopy.feature.NaturalEarthFeature(
        name="coastline",
        category="physical",
        scale="50m",
        edgecolor="#4a4435",
        facecolor="#dcd5c1",
    )
    ax.add_feature(feature)

    # Plot scatter data
    ax.scatter(
        season.Longitude,
        season.Latitude,
        c="#172C51",
        linewidth=0.3,
        marker="o",
        s=10,
        transform=ccrs.PlateCarree(),
        zorder=10,
    )

    # Subplot title
    ax.set_title(f"{name}", size=16)

    # Add panel label
    ax.text(
        0.22,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=16,
        va="bottom",
        ha="right",
    )

plt.tight_layout(rect=[0, 0, 1, 0.96])

# plt.savefig("figures/Figure7.png", transparent=True, dpi=300)

plt.show()
plt.close()
