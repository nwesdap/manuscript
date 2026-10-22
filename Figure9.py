import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Import dataset
nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")
nwes = nwes.replace([-999, "-999"], np.nan)


list_QCU_X = [
    "06GA19960613",
    "06GA20000506",
    "316N19971005",
    "45CE20180210",
    "45CE20190524",
    "45CV20180128",
    "45CV20190109",
    "58AA20010527",
    "SDG_343",
    "SDG_419",
    "SDG_550",
    "SDG_304",
    "SDG_377",
    "SDG_388",
    "SDG_389",
    "SDG_390",
    "SDG_391",
    "SDG_392",
    "SDG_394",
    "SDG_395",
    "SDG_396",
    "SDG_478",
    "SDG_479",
    "SDG_480",
    "SDG_569",
    "SDG_570",
    "DutchOA",
]

nwes_nodic = nwes.loc[
    (nwes.DIC.isnull()) & (nwes.TA_QC == 0) & ~(nwes.Name_ID.isin(list_QCU_X))
]

nwes_dic = nwes.loc[
    nwes.DIC.notnull()
    & (nwes.TA_QC == 0)
    & (nwes.DIC_QC == 0)
    & ~(nwes.Name_ID.isin(list_QCU_X))
]

nwes_dic_alk = nwes.loc[
    (nwes.TA_QC == 0)
    & (nwes.DIC_QC == 0)
    & (nwes.pH_T_insitu.isnull())
    & ~(nwes.Name_ID.isin(list_QCU_X))
]

nwes_dic_alk_pH = nwes.loc[
    (nwes.TA_QC == 0)
    & (nwes.DIC_QC == 0)
    & (nwes.pH_T_insitu_QC == 0)
    & ~(nwes.Name_ID.isin(list_QCU_X))
]

nwes_pH = nwes.loc[(nwes.pH_T_insitu_QC == 0)]
nwes_pH = nwes_pH.sort_values(by="Distance_to_shore")

# %%

fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(12, 16),
    gridspec_kw={"height_ratios": [1, 1, 0.7]},
    dpi=300,
)

labels = ["(a)", "(b)", "(c)"]

for ax, label in zip(axes.flatten(), labels):
    ax.text(
        0.1,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=20,
        va="bottom",
        ha="right",
    )


# Subplot 1
ax1 = axes[0]
ax1.set_box_aspect(1)

ax1.scatter(
    nwes_nodic.CTDSAL,
    nwes_nodic.TA,
    s=30,
    c="k",
    alpha=0.6,
    edgecolor="none",
)

graph1 = ax1.scatter(
    nwes_dic.CTDSAL,
    nwes_dic.TA,
    s=30,
    c=nwes_dic.DIC,
    cmap="viridis",
    vmin=0,
    vmax=5000,
)

cbar1 = fig.colorbar(
    graph1,
    ax=ax1,
)
cbar1.set_label("DIC (µmol kg$^{-1}$)", rotation=90, size=20)
cbar1.ax.tick_params(labelsize=17)


ax1.set_ylabel("TA (µmol kg$^{-1}$)", size=20)
ax1.set_xlabel("Salinity", size=20)
ax1.tick_params(labelsize=17)
ax1.set_xlim(-1, 39)

# Subplot 2
ax2 = axes[1]
ax2.set_box_aspect(1)
ax2.scatter(
    nwes_dic_alk.DIC,
    nwes_dic_alk.TA,
    s=30,
    c="k",
    alpha=0.6,
    edgecolor="none",
)

graph2 = ax2.scatter(
    nwes_dic_alk_pH.DIC,
    nwes_dic_alk_pH.TA,
    s=30,
    c=nwes_dic_alk_pH.pH_T_insitu,
    cmap="viridis",
)

cbar2 = fig.colorbar(
    graph2,
    ax=ax2,
)
cbar2.set_label("pH_T_insitu", rotation=90, size=20)
cbar2.ax.tick_params(labelsize=17)

ax2.set_ylabel("TA (µmol kg$^{-1}$)", size=20)
ax2.set_xlabel("DIC (µmol kg$^{-1}$)", size=20)
ax2.tick_params(labelsize=17)

# Subplot 3
ax3 = axes[2]
ax3.set_box_aspect(0.7)

graph3 = ax3.scatter(
    nwes_pH.Datetime,
    nwes_pH.pH_T_insitu,
    s=20,
    c=nwes_pH.Distance_to_shore,
    cmap="viridis",
    vmin=0,
    vmax=300,
)

cbar3 = fig.colorbar(
    graph3,
    ax=ax3,
)
cbar3.set_label("Distance to shore (km)", rotation=90, size=20)
cbar3.ax.tick_params(labelsize=17)

ax3.set_ylabel("pH_T_insitu", size=20)
ax3.set_xlabel("Date", size=20)
ax3.tick_params(labelsize=17)

plt.tight_layout()

# plt.savefig("figures/Figure9.png", transparent=True, dpi=600)

plt.show()
