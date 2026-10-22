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

# %%

allvars = [
    "DIC",
    "TA",
    "pH_T_insitu",
    "CTDOXY",
    "Nitrate",
    "Nitrite",
    "Ammonium",
    "Silicate",
    "Phosphate",
]

panel_labels = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)", "(i)"]

noProj = ccrs.PlateCarree()
myProj = ccrs.Robinson()
myProj._threshold = myProj._threshold / 20.0

fig, axes = plt.subplots(
    nrows=3,
    ncols=3,
    figsize=(15, 12),
    dpi=300,
    subplot_kw={"projection": myProj},
)

axes_flat = axes.flatten()

for i, onevar in enumerate(allvars):
    ax = axes_flat[i]

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
    ax.set_boundary(polygon)

    ax.add_feature(cfeature.OCEAN, facecolor="white")

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
    gl.xlabels_top = False

    ax.coastlines(resolution="10m", linewidth=0.1)

    feature = cartopy.feature.NaturalEarthFeature(
        name="coastline",
        category="physical",
        scale="50m",
        edgecolor="#4a4435",
        facecolor="#dcd5c1",
    )
    ax.add_feature(feature)

    ax.set_title(f"{onevar}", size=16)

    parameter = nwes.loc[(nwes[onevar].notnull())]

    ax.scatter(
        parameter.Longitude,
        parameter.Latitude,
        c="#172C51",
        linewidth=0.3,
        marker="o",
        s=6,
        transform=ccrs.PlateCarree(),
        zorder=10,
    )

    ax.text(
        0.22,
        1.01,
        panel_labels[i],
        transform=ax.transAxes,
        fontsize=16,
        va="bottom",
        ha="right",
    )

plt.tight_layout(rect=[0, 0, 1, 0.97])

# plt.savefig("figures/Figure8.png", transparent=True, dpi=600)

plt.show()
plt.close()
