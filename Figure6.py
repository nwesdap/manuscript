import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Import dataset
nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")
nwes = nwes.replace([-999, "-999"], np.nan)

nwes_poly_carb = nwes.query(
    "not(TA.isnull() & DIC.isnull() & pH_T_insitu.isnull())"
)

glodap = nwes_poly_carb.loc[nwes_poly_carb.Dataset_origin == "GLODAP"]
# %%
fig, (ax1, ax2) = plt.subplots(
    2,
    1,
    sharex=True,
    gridspec_kw={"hspace": 0},
    figsize=(4, 5),
    layout="constrained",
)

ylim1 = (0, 100)
ylim2 = (100, 1000)

bins1 = np.arange(ylim1[0], ylim1[1] + 1, (ylim1[1] - ylim1[0]) / 20)
bins2 = np.arange(ylim2[0], ylim2[1] + 1, (ylim2[1] - ylim2[0]) / 18)

ax1.hist(
    nwes_poly_carb.Depth,
    bins=bins1,
    orientation="horizontal",
    color="#343538",
    edgecolor="w",
    linewidth=0.7,
)

ax1.hist(
    glodap.Depth,
    bins=bins1,
    orientation="horizontal",
    color="#969aa1",
    edgecolor="w",
    linewidth=0.7,
)
ax2.hist(
    nwes_poly_carb.Depth,
    bins=bins2,
    orientation="horizontal",
    color="#343538",
    edgecolor="w",
    linewidth=0.7,
    label="Added in NWESDAP",
)

ax2.hist(
    glodap.Depth,
    bins=bins2,
    orientation="horizontal",
    color="#969aa1",
    edgecolor="w",
    linewidth=0.7,
    label="GLODAPv2.2023",
)

ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)
ax1.tick_params(axis="x", bottom=False)

ax1.set_ylim(ylim1[1], ylim1[0])  # Top plot: 100 at bottom, 0 at top
ax2.set_ylim(ylim2[1], ylim2[0])  # Bottom plot: 1000 at bottom, 100 at top

fig.supylabel("Depth (m)", size=11)
ax2.set_xlabel("Number of observations", size=11)
plt.xlim(0, 10000)

ax1.annotate(
    "28,458",
    xy=(9900, 6),
    xytext=(6000, 35),
    arrowprops=dict(facecolor="black", shrink=0.05),
)

plt.legend(
    loc="lower right",
    title_fontsize=8,
    fontsize=8,
)

# plt.savefig(
#     "figures/Figure6.png",
#     transparent=True,
#     dpi=300,
# )

plt.show()
