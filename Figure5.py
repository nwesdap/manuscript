import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Import dataset
nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")
nwes = nwes.replace([-999, "-999"], np.nan)

nwes_poly_carb = nwes.query(
    "not(TA.isnull() & DIC.isnull() & pH_T_insitu.isnull())"
)
# %% Classification of number of data per parameter per year and month

year_counts = nwes_poly_carb.groupby(["Year_UTC"])[
    ["TA", "DIC", "pH_T_insitu"]
].count()

month_counts = nwes_poly_carb.groupby(["Month_UTC"])[
    ["TA", "DIC", "pH_T_insitu"]
].count()


# %% Classification of number of data per parameter per year and month for GLODAP data

glodap_poly_carb = nwes_poly_carb.loc[
    nwes_poly_carb.Dataset_origin == "GLODAP"
]

year_counts_glodap = glodap_poly_carb.groupby(["Year_UTC"])[
    ["TA", "DIC", "pH_T_insitu"]
].count()

month_counts_glodap = glodap_poly_carb.groupby(["Month_UTC"])[
    ["TA", "DIC", "pH_T_insitu"]
].count()

# %%

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 10), dpi=300)

top_labels = ["(a)", "(b)", "(c)"]
bottom_labels = ["(d)", "(e)", "(f)"]

variables = ["TA", "DIC", "pH_T_insitu"]


var_settings = {
    "TA": {
        "color_product": "#E6B232",
        "color_glodap": "#F0D17A",
    },
    "DIC": {
        "color_product": "#172C51",
        "color_glodap": "#6A869B",
    },
    "pH_T_insitu": {
        "color_product": "#6BAFAF",
        "color_glodap": "#BFE4E4",
    },
}

for i, var in enumerate(variables):
    settings = var_settings[var]

    # Yearly distribution
    ax_top = axes[0, i]

    ax_top.bar(
        year_counts.index,
        year_counts[var],
        width=1,
        color=settings["color_product"],
        edgecolor="white",
        linewidth=0.7,
        label="Added in NWESDAP",
    )
    ax_top.bar(
        year_counts_glodap.index,
        year_counts_glodap[var],
        width=1,
        color=settings["color_glodap"],
        edgecolor="white",
        linewidth=0.7,
        label="GLODAPv2.2023",
    )

    ax_top.tick_params(axis="both", labelsize=17)
    ax_top.set_xlabel("Year", size=17)
    ax_top.set_ylabel("Number of observations", size=17)
    ax_top.set_title(var, size=19)
    ax_top.set_xlim(1974, 2027)
    ax_top.set_ylim(0, 2200)
    ax_top.legend(loc="upper left", fontsize=12)

    ax_top.text(
        0.07,
        1.01,
        top_labels[i],
        transform=ax_top.transAxes,
        fontsize=19,
        va="bottom",
        ha="right",
    )
    # Monthly distribution
    ax_bottom = axes[1, i]

    ax_bottom.bar(
        month_counts.index,
        month_counts[var],
        width=1,
        color=settings["color_product"],
        edgecolor="white",
        linewidth=0.7,
        label="This product",
    )
    ax_bottom.bar(
        month_counts_glodap.index,
        month_counts_glodap[var],
        width=1,
        color=settings["color_glodap"],
        edgecolor="white",
        linewidth=0.7,
        label="GLODAP",
    )

    ax_bottom.tick_params(axis="both", labelsize=17)
    ax_bottom.set_xlabel("Month", size=17)
    ax_bottom.set_ylabel("Number of observations", size=17)
    ax_bottom.set_ylim(0, 3200)
    ax_bottom.set_xlim(0.5, 12.5)
    ax_bottom.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    ax_bottom.text(
        0.07,
        1.01,
        bottom_labels[i],
        transform=ax_bottom.transAxes,
        fontsize=19,
        va="bottom",
        ha="right",
    )
plt.tight_layout()

# plt.savefig(
#     "figures/Figure5.png",
#     transparent=True,
#     dpi=300,
# )


plt.show()
