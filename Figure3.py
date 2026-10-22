import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.optimize import least_squares
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import qctools as qct

# Import dataset
nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")

assert nwes.index.notnull().all()

tvars = ["pH_T_insitu"]

# minimum and maximum MLR window, TODO tweak per cruise
window = {
    "CTDSAL": [2, 2],
    "CTDTEMP": [2, 2],
    "Datenum": [30, 30],
    "Depth": [10, 10],
    "Distance_to_shore": [5, 20],
    "Latitude": [1, 1],
    "Longitude": [1, 1],
}

# ranges of values for other cruises to compare MLR with
min_ranges = {
    "Datenum": 1,
    "Depth": 1,
    "Distance_to_shore": 5,
    "Latitude": 0.1,
    "Longitude": 0.1,
}


# plotting settings for flags
QC_settings = {
    0: {
        "colour": "xkcd:midnight",
        "marker": "o",
        "size": 40,
        "label": "flag 0",
    },
    3: {
        "colour": "xkcd:fire engine red",
        "marker": "*",
        "size": 100,
        "label": "flag 3",
    },
}

# saving and showing figures
save = False
show = True

# %%

Name_ID = "11BG20070510"
for i, (ido, qcu) in enumerate(
    [[Name_ID, nwes[nwes.Name_ID == Name_ID].copy()]], start=1
):

    for tvar in tvars:
        L = qcu[tvar].notnull()
        L &= qcu[tvar + "_QC"] == 0
        for v in window:
            L &= qcu[v].notnull()
        if L.sum() >= 50:  # how many data points are minimum for an MLR
            predictors = {}
            predictors["CTDSAL"] = qcu[L].CTDSAL.to_numpy()
            predictors["CTDTEMP"] = qcu[L].CTDTEMP.to_numpy()
            for v, mr in min_ranges.items():
                v_values = qcu[L][v].to_numpy()
                if v_values.max() - v_values.min() > mr:
                    predictors[v] = v_values
            target = qcu[L][tvar].to_numpy()

            # Make MLR for this QCU
            def get_target(c, predictors):
                p = predictors
                t = (
                    c[0]
                    + c[1] * p["CTDSAL"]
                    + c[2] * p["CTDSAL"] ** 2
                    + c[3] * p["CTDTEMP"]
                    + c[4] * p["CTDTEMP"] ** 2
                    + c[5] * p["CTDSAL"] * p["CTDTEMP"]
                )
                j = 6
                if "Datenum" in p:
                    t += c[j] * p["Datenum"]
                    j += 1
                if "Depth" in p:
                    t += c[j] * p["Depth"] + c[j + 1] * p["Depth"] ** 2
                    j += 2
                if "Distance_to_shore" in p:
                    t += (
                        c[j] * p["Distance_to_shore"]
                        + c[j + 1] * p["Distance_to_shore"] ** 2
                    )
                    j += 2
                if "Latitude" in p:
                    t += c[j] * p["Latitude"]
                    j += 1
                if "Longitude" in p:
                    t += c[j] * p["Longitude"]
                    j += 1
                return t

            def _lsqfun_get_target(c, predictors, target):
                return get_target(c, predictors) - target

            optr = least_squares(
                _lsqfun_get_target,
                [0] * 13,
                args=(predictors, target),
            )
            predicted = get_target(optr.x, predictors)

            predicted_all = get_target(
                optr.x, {k: qcu[k].to_numpy() for k in predictors}
            )
            # set offset between measured and predicted as new variable qcu["offset"]
            qcu["offset"] = predicted_all - qcu[tvar]

            # flag suspicious datapoints
            qc_count = qcu[tvar].notnull().sum()
            if qc_count > 0:
                qc_median = np.median(predicted - target)
                qc_stdSn = qct.std_Sn(predicted - target)


fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
savename = f"{ido}_{tvar}"

# plot flagged points with different color and shape
for QC, QCs in QC_settings.items():
    ax.scatter(
        tvar,
        "offset",
        data=qcu[qcu[tvar + "_QC"] == QC],
        marker=QCs["marker"],
        c=QCs["colour"],
        s=QCs["size"],
        alpha=0.8,
        label=QCs["label"],
        zorder=10,
    )

ax.legend(
    bbox_to_anchor=(0.98, 0.98),
    borderaxespad=0.0,
    title="Flags",
    title_fontsize=12,
    fontsize=12,
    facecolor="white",
    framealpha=1,
)
ax.tick_params(axis="both", which="major", labelsize=18)
ax.xaxis.label.set_size(18)
ax.yaxis.label.set_size(18)
ax.title.set_size(18)


xlim = ax.get_xlim()
for offset in range(1, 5):
    ax.fill_between(
        xlim,
        qc_median - offset * qc_stdSn,
        qc_median + offset * qc_stdSn,
        facecolor="xkcd:navy",
        alpha=0.2,
    )
ax.set_xlim(8.038, 8.178)
ax.set_xlabel("measured pH_T_insitu")
ax.set_ylabel("MLR prediction $-$ measured value")
# ax.set_title(title)
ax.tick_params(axis="both", which="major", labelsize=18)
ax.xaxis.label.set_size(18)
ax.yaxis.label.set_size(18)
ax.title.set_size(18)
ax.axhline(0, c="k", lw=0.8)
ax.grid(alpha=0.2)

fig.tight_layout()
# fig.savefig("figures/Figure3.png")
