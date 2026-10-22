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


# %% Figure S1 - Seasonal distribution TA

seasons_TA = {
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

for name, (seasons_TA, row, col, label) in seasons_TA.items():
    ax = axes[row, col]

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

    ax.coastlines(resolution="10m", linewidth=0.1)

    feature = cartopy.feature.NaturalEarthFeature(
        name="coastline",
        category="physical",
        scale="50m",
        edgecolor="#4a4435",
        facecolor="#dcd5c1",
    )
    ax.add_feature(feature)

    seasons_TA = seasons_TA.loc[seasons_TA.TA.notnull()]

    ax.scatter(
        seasons_TA.Longitude,
        seasons_TA.Latitude,
        c="#172C51",
        linewidth=0.3,
        marker="o",
        s=10,
        transform=ccrs.PlateCarree(),
        zorder=10,
    )

    ax.set_title(f"{name}", size=16)

    ax.text(
        0.22,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=16,
        va="bottom",
        ha="right",
    )

fig.suptitle(
    "Seasonal distribution TA",
    fontsize=23,
    y=0.95,
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig("figures/FigureS1.png", dpi=300)
plt.show()
plt.close()


# %% Figure S2 - Seasonal distribution DIC

seasons_DIC = {
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

for name, (seasons_DIC, row, col, label) in seasons_DIC.items():
    ax = axes[row, col]

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

    ax.coastlines(resolution="10m", linewidth=0.1)

    feature = cartopy.feature.NaturalEarthFeature(
        name="coastline",
        category="physical",
        scale="50m",
        edgecolor="#4a4435",
        facecolor="#dcd5c1",
    )
    ax.add_feature(feature)

    seasons_DIC = seasons_DIC.loc[seasons_DIC.DIC.notnull()]

    ax.scatter(
        seasons_DIC.Longitude,
        seasons_DIC.Latitude,
        c="#172C51",
        linewidth=0.3,
        marker="o",
        s=10,
        transform=ccrs.PlateCarree(),
        zorder=10,
    )

    ax.set_title(f"{name}", size=16)

    ax.text(
        0.22,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=16,
        va="bottom",
        ha="right",
    )

fig.suptitle(
    "Seasonal distribution DIC",
    fontsize=23,
    y=0.95,
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig("figures/FigureS2.png", dpi=300)
plt.show()
plt.close()


# %% Figure S3 - Seasonal distribution pH_T_insitu

seasons_pH = {
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

for name, (seasons_pH, row, col, label) in seasons_pH.items():
    ax = axes[row, col]

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

    ax.coastlines(resolution="10m", linewidth=0.1)

    feature = cartopy.feature.NaturalEarthFeature(
        name="coastline",
        category="physical",
        scale="50m",
        edgecolor="#4a4435",
        facecolor="#dcd5c1",
    )
    ax.add_feature(feature)

    seasons_pH = seasons_pH.loc[seasons_pH.pH_T_insitu.notnull()]

    ax.scatter(
        seasons_pH.Longitude,
        seasons_pH.Latitude,
        c="#172C51",
        linewidth=0.3,
        marker="o",
        s=10,
        transform=ccrs.PlateCarree(),
        zorder=10,
    )

    ax.set_title(f"{name}", size=16)

    ax.text(
        0.22,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=16,
        va="bottom",
        ha="right",
    )

fig.suptitle(
    "Seasonal distribution pH_T_insitu",
    fontsize=23,
    y=0.95,
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig("figures/FigureS3.png", dpi=300)
plt.show()
plt.close()
