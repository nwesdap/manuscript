# %%
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import qctools as qct
import cartopy.crs as ccrs
import cartopy.feature as cfeature


nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")

nwes = nwes.replace([-999, "-999"], np.nan)

nwes = nwes.rename(
    columns={
        "DIC": "DIC (µmol kg$^{-1}$)",
        "DIC_QC": "DIC (µmol kg$^{-1}$)_QC",
        "TA": "TA (µmol kg$^{-1}$)",
        "Depth": "Depth (m)",
        "CTDTEMP": "CTDTEMP (°C)",
    }
)

qcvars = ["DIC (µmol kg$^{-1}$)"]

# How many stds away from the mean = bad
qc_stats_limit = 4

# plotting settings for flags
ipf_settings = {
    0: {
        "colour": "xkcd:midnight",
        "marker": "o",
        "size": 40,
        "label": "QC flag 0",
    },
    2: {
        "colour": "gold",
        "marker": "*",
        "size": 150,
        "label": "QC flag 2",
    },
}

id_count = len(nwes.Name_ID.unique())

# saving and showing figures
save = False
show = True

# %%
# to test, use only one cruise
test = nwes.loc[(nwes.Name_ID == "NorwegianWestCoast_2020_2021")]

# to loop trough all variables:
for i, (ido, qcu) in enumerate(test.groupby("Name_ID"), start=1):
    print(f"{i} of {id_count} ({ido})")

    for qcvar in qcvars:
        # Calculate statistics
        qc_count = qcu[qcvar].notnull().sum()
        if qc_count > 0:
            qc_median = qcu[qcvar].median()
            qc_stdSn = qct.std_Sn(qcu[qcvar].to_numpy())

            for xvar in [
                "Depth (m)",
                "CTDSAL",
                "TA (µmol kg$^{-1}$)",
                "CTDTEMP (°C)",
            ]:
                if xvar != qcvar:
                    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)

                    for ipf, ipfs in ipf_settings.items():
                        ax.scatter(
                            xvar,
                            qcvar,
                            data=qcu[qcu[qcvar + "_QC"] == ipf],
                            marker=ipfs["marker"],
                            c=ipfs["colour"],
                            s=ipfs["size"],
                            label=ipfs["label"],
                            alpha=0.8,
                            # label=ipf,
                            zorder=10,
                        )
                    ax.tick_params(axis="both", which="major", labelsize=17)
                    ax.xaxis.label.set_size(20)
                    ax.yaxis.label.set_size(20)
                    ax.title.set_size(14)
                    ax.axhline(qc_median, c="xkcd:navy", lw=2)

                    xlim = ax.get_xlim()
                    for offset in range(1, 5):
                        ax.fill_between(
                            xlim,
                            qc_median - offset * qc_stdSn,
                            qc_median + offset * qc_stdSn,
                            facecolor="xkcd:navy",
                            alpha=0.2,
                            zorder=8,
                        )
                    ax.set_xlim(xlim)

                    ax.grid(alpha=0.4)
                    ax.set_xlabel(xvar)
                    ax.set_ylabel(qcvar)
                    fig.tight_layout()

                    if save:
                        fig.savefig(
                            f"figures/Figure2_{ido}_{qcvar}_{xvar}.png"
                        )

                    if show:
                        plt.show()
                    plt.close()

# %%
qcvar = "DIC (µmol kg$^{-1}$)"
xvar = "Datetime"
# for qcvar in qcvars:
qc_count = qcu[qcvar].notnull().sum()
if qc_count > 0:
    qc_median = qcu[qcvar].median()
    qc_stdSn = qct.std_Sn(qcu[qcvar].to_numpy())

    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)

    for ipf, ipfs in ipf_settings.items():
        ax.scatter(
            xvar,
            qcvar,
            data=qcu[qcu[qcvar + "_QC"] == ipf],
            marker=ipfs["marker"],
            c=ipfs["colour"],
            s=ipfs["size"],
            label=ipfs["label"],
            alpha=0.8,
            zorder=10,
        )
    ax.tick_params(axis="both", which="major", labelsize=17)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    ax.set_xlabel("Datetime")
    ax.set_ylabel("DIC (µmol kg$^{-1}$)")
    ax.xaxis.label.set_size(20)
    ax.yaxis.label.set_size(20)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.axhline(qc_median, c="xkcd:navy", lw=2)

    xlim = ax.get_xlim()
    for offset in range(1, 5):
        ax.fill_between(
            xlim,
            qc_median - offset * qc_stdSn,
            qc_median + offset * qc_stdSn,
            facecolor="xkcd:navy",
            alpha=0.2,
            zorder=8,
        )
    ax.set_xlim(xlim)

    ax.grid(alpha=0.4)

    legend = ax.legend(
        loc="upper right",
        title="Flags",
        facecolor="white",
        framealpha=1,
    ).set_zorder(11)

    fig.tight_layout()

    if save:
        fig.savefig(f"figures/Figure2_{ido}_{qcvar}_{xvar}.png")

    if show:
        plt.show()
    plt.close()


# %% Map (Figure 2a)
plt.figure(dpi=300, figsize=(9, 7))

ax = plt.axes(projection=ccrs.Miller())
ax.set_extent([0, 15, 56.5, 67])

# Map features
ax.add_feature(cfeature.LAND, edgecolor="grey", facecolor="lightgrey")
ax.add_feature(cfeature.COASTLINE, edgecolor="dimgrey")
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.coastlines(resolution="10m", linewidth=0.1)

# map settings
gl = ax.gridlines(
    linestyle="--",
    color="lightgrey",
    draw_labels=True,
)
gl.xlabels_top = False
gl.ylabels_right = False
gl.xlabel_style = {"size": 20}
gl.ylabel_style = {"size": 20}

ax.scatter(
    qcu.Longitude,
    qcu.Latitude,
    c="mediumblue",
    marker="o",
    edgecolor="xkcd:midnight",
    s=100,
    transform=ccrs.PlateCarree(),
    zorder=10,
)

plt.title("NorwegianWestCoast_2020_2021", fontsize=20)

# plt.savefig("figures/Figure2a.png", transparent=True, dpi=600)
