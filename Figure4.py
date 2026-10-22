import pandas as pd
import numpy as np
import PyCO2SYS as pyco2
from pyco2_kwargs import pyco2_kwargs
from matplotlib import pyplot as plt

# Open NWESDAP
nwesdap = pd.read_parquet("data/NWESDAP_v20102026.parquet")

# Select only datapoints with values for the three carbonate system variables
carb = nwesdap.loc[
    (nwesdap.TA != -999)
    & (nwesdap.DIC != -999)
    & (nwesdap.pH_T_insitu != -999)
]

# create nutrient columns for carbonate system calculations with 0 when no value
carb["Silicate_calc"] = np.where(
    carb["Silicate"] == -999,
    0,
    carb["Silicate"],
)

carb["Phosphate_calc"] = np.where(
    carb["Phosphate"] == -999,
    0,
    carb["Phosphate"],
)

carb["Ammonium_calc"] = np.where(
    carb["Ammonium"] == -999,
    0,
    carb["Ammonium"],
)

# %% Calculate carb params

carb["TA"] = np.where(carb.TA <= 0, np.nan, carb["TA"])
carb["DIC"] = np.where(carb.DIC <= 0, np.nan, carb["DIC"])
carb["pH_T_insitu"] = np.where(
    carb.pH_T_insitu < 6, np.nan, carb["pH_T_insitu"]
)


carb["TA_calculated"] = pyco2.sys(
    par1=carb.DIC,
    par1_type=2,
    par2=carb.pH_T_insitu,
    par2_type=3,
    salinity=carb.CTDSAL,
    temperature=carb.CTDTEMP,
    pressure=carb.CTDPRES,
    total_silicate=carb.Silicate_calc,
    total_phosphate=carb.Phosphate_calc,
    total_ammonia=carb.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["alkalinity"]

carb["DIC_calculated"] = pyco2.sys(
    par1=carb.TA,
    par1_type=1,
    par2=carb.pH_T_insitu,
    par2_type=3,
    salinity=carb.CTDSAL,
    temperature=carb.CTDTEMP,
    pressure=carb.CTDPRES,
    total_silicate=carb.Silicate_calc,
    total_phosphate=carb.Phosphate_calc,
    total_ammonia=carb.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["dic"]

carb["pH_T_insitu_calculated"] = pyco2.sys(
    par1=carb.DIC,
    par1_type=2,
    par2=carb.TA,
    par2_type=1,
    salinity=carb.CTDSAL,
    temperature=carb.CTDTEMP,
    pressure=carb.CTDPRES,
    total_silicate=carb.Silicate_calc,
    total_phosphate=carb.Phosphate_calc,
    total_ammonia=carb.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["pH_total"]


# Create new columns with difference between calculated and measured values
carb["TA_diff"] = carb.TA_calculated - carb.TA
carb["DIC_diff"] = carb.DIC_calculated - carb.DIC
carb["pH_T_insitu_diff"] = carb.pH_T_insitu_calculated - carb.pH_T_insitu
# %% Detect if one of the carb param is flagged as questionnable from one of the QC steps

# Create new column with info on data quality

# QC = 2 for datapoint with the three variables = good data
# if one variable has a QC flag > 0, then QC = 3
condition = (
    (carb["TA_QC"] == 0)
    & (carb["DIC_QC"] == 0)
    & (carb["pH_T_insitu_QC"] == 0)
)

carb["QC"] = np.where(condition, 2, 3)

# QC = 4 for datapoint with at least one of the carbonate system variable with a _QC => 2
condition = (
    (carb["TA_QC"] > 1) | (carb["DIC_QC"] > 1) | (carb["pH_T_insitu_QC"] > 1)
)

carb["QC"] = np.where(condition, 4, carb["QC"])

# QC = 5 if at least one of the variable has uncertainties greater than weather-quality goal
condition = (
    (carb["TA_QCU_flag"] == "X")
    | (carb["DIC_QCU_flag"] == "X")
    | (carb["pH_T_insitu_QCU_flag"] == "X")
)

carb["QC"] = np.where(condition, 5, carb["QC"])

# Create a subdataframe with only data with good quality
carbclean = carb.loc[(carb.QC == 2)]


# %%
fig, axs = plt.subplots(3, 3, figsize=(22, 20), dpi=600)


labels = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)", "(i)"]

# Loop through flattened axes and labels
for ax, label in zip(axs.flatten(), labels):
    ax.text(
        0.07,
        1.01,
        label,
        transform=ax.transAxes,
        fontsize=20,
        va="bottom",
        ha="right",
    )

qcvars = ["TA", "DIC", "pH_T_insitu"]
ipf_settings = {
    5: {
        "color": "darkgrey",
        "edgecolor": "darkgrey",
        "facecolor": "darkgrey",
        "marker": "x",
        "size": 30,
        "label": "QCU flag X",
    },
    2: {
        "edgecolor": "xkcd:dark grey",
        "facecolor": "none",
        "marker": "o",
        "size": 30,
        "label": "QC flag 0",
    },
    3: {
        "color": "xkcd:french blue",
        "edgecolor": "xkcd:french blue",
        "facecolor": "xkcd:french blue",
        "marker": "*",
        "size": 30,
        "label": "QC flag 1",
    },
    4: {
        "color": "r",
        "edgecolor": "r",
        "facecolor": "r",
        "marker": "*",
        "size": 30,
        "label": "QC flag 2, 3",
    },
}


qcvar1 = qcvars[0]
diff_col1 = f"{qcvar1}_diff"
flag_col = "QC"

if carb[diff_col1].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carb[carb[flag_col] == ipf]
        if not plot_data.empty:
            axs[0, 0].scatter(
                plot_data[qcvar1],
                plot_data[diff_col1],
                marker=ipfs["marker"],
                # c=ipfs["color"],
                facecolor=ipfs["facecolor"],
                edgecolor=ipfs["edgecolor"],
                s=ipfs["size"],
                alpha=0.8,
                label=ipfs["label"],
                zorder=10,
            )
    axs[0, 0].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[0, 0].set_xlabel("TA (µmol kg$^{-1}$)", fontsize=17)
    axs[0, 0].set_ylabel(
        f"{qcvar1} calculated $-$ {qcvar1} measured", fontsize=17
    )
    axs[0, 0].set_title(f"{qcvar1} internal consistency", fontsize=19)
    axs[0, 0].set_xlim(1100, 2900)
    axs[0, 0].tick_params(labelsize=17)
    axs[0, 0].grid(alpha=0.3)

qcvar2 = qcvars[1]
diff_col2 = f"{qcvar2}_diff"

if carb[diff_col2].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carb[carb[flag_col] == ipf]
        if not plot_data.empty:
            axs[0, 1].scatter(
                plot_data[qcvar2],
                plot_data[diff_col2],
                marker=ipfs["marker"],
                # c=ipfs["color"],
                facecolor=ipfs["facecolor"],
                edgecolor=ipfs["edgecolor"],
                s=ipfs["size"],
                alpha=0.8,
                label=ipfs["label"],
                zorder=10,
            )
    axs[0, 1].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[0, 1].set_xlabel("DIC (µmol kg$^{-1}$)", fontsize=17)
    axs[0, 1].set_ylabel(
        f"{qcvar2} calculated $-$ {qcvar2} measured", fontsize=17
    )
    axs[0, 1].set_title(f"{qcvar2} internal consistency", fontsize=19)
    axs[0, 1].set_xlim(950, 3100)
    axs[0, 1].tick_params(labelsize=17)
    axs[0, 1].grid(alpha=0.3)


qcvar3 = qcvars[2]
diff_col3 = f"{qcvar3}_diff"

if carb[diff_col3].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carb[carb[flag_col] == ipf]
        if not plot_data.empty:
            axs[0, 2].scatter(
                plot_data[qcvar3],
                plot_data[diff_col3],
                marker=ipfs["marker"],
                # c=ipfs["color"],
                facecolor=ipfs["facecolor"],
                edgecolor=ipfs["edgecolor"],
                s=ipfs["size"],
                alpha=0.8,
                label=ipfs["label"],
                zorder=10,
            )
    axs[0, 2].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[0, 2].set_xlabel(f"{qcvar3}", fontsize=17)
    axs[0, 2].set_ylabel(
        f"{qcvar3} calculated $-$ {qcvar3} measured", fontsize=15
    )
    axs[0, 2].set_title(f"{qcvar3} internal consistency", fontsize=19)
    axs[0, 2].tick_params(labelsize=17)
    axs[0, 2].set_xlim(7.1, 8.6)
    axs[0, 2].grid(alpha=0.3)
    axs[0, 2].legend(
        title="Flags",
        title_fontsize=17,
        fontsize=17,
        bbox_to_anchor=(1.05, 1),
        loc=2,
        borderaxespad=0.0,
    )


qcvar1 = qcvars[0]
diff_col1 = f"{qcvar1}_diff"
flag_col = "QC"

if carbclean[diff_col1].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[1, 0].scatter(
                plot_data[qcvar1],
                plot_data[diff_col1],
                marker=ipfs["marker"],
                facecolor="none",
                s=ipfs["size"],
                alpha=0.9,
                edgecolor="xkcd:dark grey",
                label=ipfs["label"],
                zorder=10,
            )
    axs[1, 0].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 0].axhline(10, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 0].axhline(-10, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 0].set_xlabel("TA (µmol kg$^{-1}$)", fontsize=17)
    axs[1, 0].set_ylabel(
        f"{qcvar1} calculated $-$ {qcvar1} measured", fontsize=17
    )
    axs[1, 0].set_xlim(1100, 2900)
    axs[1, 0].tick_params(labelsize=17)
    axs[1, 0].grid(alpha=0.3)

qcvar2 = qcvars[1]
diff_col2 = f"{qcvar2}_diff"

if carbclean[diff_col2].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[1, 1].scatter(
                plot_data[qcvar2],
                plot_data[diff_col2],
                marker=ipfs["marker"],
                facecolor="none",
                s=ipfs["size"],
                alpha=0.9,
                edgecolor="xkcd:dark grey",
                label=ipfs["label"],
                zorder=10,
            )
    axs[1, 1].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 1].axhline(10, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 1].axhline(-10, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 1].set_xlabel("DIC (µmol kg$^{-1}$)", fontsize=17)
    axs[1, 1].set_ylabel(
        f"{qcvar2} calculated $-$ {qcvar2} measured", fontsize=17
    )
    axs[1, 1].set_xlim(950, 3100)
    axs[1, 1].tick_params(labelsize=17)
    axs[1, 1].grid(alpha=0.3)


qcvar3 = qcvars[2]
diff_col3 = f"{qcvar3}_diff"

if carbclean[diff_col3].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[1, 2].scatter(
                plot_data[qcvar3],
                plot_data[diff_col3],
                marker=ipfs["marker"],
                facecolor="none",
                s=ipfs["size"],
                alpha=0.9,
                edgecolor="xkcd:dark grey",
                label=ipfs["label"],
                zorder=10,
            )
    axs[1, 2].axhline(0, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 2].axhline(0.02, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 2].axhline(-0.02, c="xkcd:navy", lw=1.5, ls="--", alpha=0.7)
    axs[1, 2].set_xlabel(f"{qcvar3}", fontsize=17)
    axs[1, 2].set_ylabel(
        f"{qcvar3} calculated $-$ {qcvar3} measured", fontsize=15
    )
    axs[1, 2].set_xlim(7.1, 8.6)
    axs[1, 2].tick_params(labelsize=17)
    axs[1, 2].grid(alpha=0.3)

qcvar1 = qcvars[0]
diff_col1 = f"{qcvar1}_diff"
flag_col = "QC"

if carbclean[diff_col1].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[2, 0].hist(
                plot_data[diff_col1],
                bins=300,
                color="xkcd:dark grey",
                zorder=10,
                orientation="horizontal",
            )
    axs[2, 0].set_ylim(-50, 50)
    axs[2, 0].axhline(
        0, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 0].axhline(
        10, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 0].axhline(
        -10, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 0].set_ylabel(
        f"{qcvar1} calculated $-$ {qcvar1} measured", fontsize=17
    )
    axs[2, 0].tick_params(labelsize=17)
    axs[2, 0].grid(alpha=0.3)

qcvar2 = qcvars[1]
diff_col2 = f"{qcvar2}_diff"

if carbclean[diff_col2].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[2, 1].hist(
                plot_data[diff_col2],
                bins=200,
                color="xkcd:dark grey",
                label=ipfs["label"],
                zorder=10,
                orientation="horizontal",
            )
    axs[2, 1].set_ylim(-50, 50)
    axs[2, 1].axhline(
        0, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 1].axhline(
        10, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 1].axhline(
        -10, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 1].set_ylabel(
        f"{qcvar2} calculated $-$ {qcvar2} measured", fontsize=17
    )
    axs[2, 1].tick_params(labelsize=17)
    axs[2, 1].grid(alpha=0.3)


qcvar3 = qcvars[2]
diff_col3 = f"{qcvar3}_diff"

if carbclean[diff_col3].notnull().any():
    for ipf, ipfs in ipf_settings.items():
        plot_data = carbclean[carbclean[flag_col] == ipf]
        if not plot_data.empty:
            axs[2, 2].hist(
                plot_data[diff_col3],
                bins=200,
                color="xkcd:dark grey",
                label=ipfs["label"],
                zorder=10,
                orientation="horizontal",
            )
    axs[2, 2].set_ylim(-0.1, 0.1)
    axs[2, 2].axhline(
        0, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 2].axhline(
        0.02, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 2].axhline(
        -0.02, c="xkcd:silver", lw=1.5, ls="--", alpha=0.7, zorder=11
    )
    axs[2, 2].set_ylabel(
        f"{qcvar3} calculated $-$ {qcvar3} measured", fontsize=15
    )
    axs[2, 2].tick_params(labelsize=17)
    axs[2, 2].grid(alpha=0.3)


plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# plt.savefig(
#     "figures/Figure4.png",
#     transparent=True,
#     dpi=300,
# )

plt.show()
plt.close(fig)
