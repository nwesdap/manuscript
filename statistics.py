"""
Statistics for NWESDAP manuscript
"""

import pandas as pd
import numpy as np
import PyCO2SYS as pyco2
from pyco2_kwargs import pyco2_kwargs

# %% General numbers

nwes = pd.read_parquet("data/NWESDAP_v20102026.parquet")

nwes = nwes.replace([-999, "-999"], np.nan)

print(f"\nNumber of datapoints in NWESDAP:\n{len(nwes)}")

glodap = nwes.loc[nwes.Dataset_origin == "GLODAP"]

print(f"\nNumber of datapoints from GLODAP in NWESDAP:\n{len(glodap)}")

print(
    f"\nPercentage of data available in GLODAPv2.2023 in NWESDAP:\n{len(glodap)*100/len(nwes)}"
)

print(
    f"\nNumber of units (Name_ID) in NWESDAP:\n{len(nwes.Name_ID.unique())}"
)

print(
    f"\nYears covered by NWESDAP:\n{nwes.Year_UTC.min()} to {nwes.Year_UTC.max()}"
)

# %% Number of datapoints of at least weather quality

metadata = pd.read_excel("data/NWESDAP_metadata_v20102026.xlsx")

metadata = metadata.replace(["Z"], np.nan)

# Define the priority mapping (X is highest, W is middle, C is lowest)
priority_map = {"X": 3, "W": 2, "C": 1}
reverse_map = {3: "X", 2: "W", 1: "C"}

qc_cols = ["DIC_QCU_flag", "TA_QCU_flag", "pH_T_insitu_QCU_flag"]
numeric_qc = metadata[qc_cols].replace(priority_map).fillna(0)
max_numeric = numeric_qc.max(axis=1)

# Map the highest number back to the letter
metadata["GOA_ON_QC"] = max_numeric.map(reverse_map).fillna("")

# Add column to dataset to evaluate the number of datapoint per GOA-ON quality level
unit_id = dict(zip(metadata["Unit_ID"], metadata["GOA_ON_QC"]))
nwes["GOA_ON_QC"] = nwes["Unit_ID"].map(unit_id)

qc_counts = nwes["GOA_ON_QC"].value_counts(dropna=False)
print(qc_counts)

print(
    f"\nNumber of datapoints of at least weather quality:\n{qc_counts.iloc[1] + qc_counts.iloc[2]}"
)

# %% Number of QCU with original flag

original_flag = nwes.loc[
    (nwes.DIC_flagPI != 10)
    | (nwes.TA_flagPI != 10)
    | (nwes.pH_T_insitu_flagPI != 10)
]

print(
    f"\nNumber of QCU with original flags: {len(original_flag.Unit_ID.unique())}"
)

print(
    f"\nNumber of QCU without original flags: {len(nwes.Unit_ID.unique()) - len(original_flag.Unit_ID.unique())}"
)

# %% Number of QCUs per variable
variables = ["TA", "DIC", "pH_T_insitu"]

cruise_counts = {}
for var in variables:
    if var in nwes.columns:
        valid_cruises = nwes[nwes[var].notnull()]["Name_ID"].nunique()
        cruise_counts[var] = valid_cruises
    else:
        cruise_counts[var] = 0

print("--- Number of Cruises per Parameter ---")
for var, count in cruise_counts.items():
    print(f"Cruises with {var} data: {count}")


all_three = nwes.loc[
    (nwes.DIC.notnull()) & (nwes.TA.notnull()) & (nwes.pH_T_insitu.notnull())
]

all_three_nb = all_three["Name_ID"].nunique()
print(f"\nCruises with all three parameters: {all_three_nb}")

print(
    f"\nNumber of datapoints with the three carbonate system variables: {len(all_three)}"
)

print(
    f"\nPercentage of datapoints with the three carbonate system variables: {len(all_three)*100/len(nwes)}"
)
# %% Number of each QC flag per carbonate system variable

flags_alk = nwes.groupby(["TA_QC"])[["CTDTEMP"]].count()
print(f"\nnumber of flags for TA:\n{flags_alk}")

flags_dic = nwes.groupby(["DIC_QC"])[["DIC"]].count()
print(f"\nnumber of flags for DIC:\n{flags_dic}")

flags_pH = nwes.groupby(["pH_T_insitu_QC"])[["pH_T_insitu"]].count()
print(f"\nnumber of flags for pH:\n{flags_pH}")


# %% Number of QCUs with > 50 datapoints per carbonate system variable

carb_counts_unit = nwes.groupby(["Name_ID", "Unit_ID"])[
    ["TA", "DIC", "pH_T_insitu"]
].count()

print(
    f"\nNumber of datapoints per carbonate system parameter per QCU:\n{carb_counts_unit}"
)

cols = ["TA", "DIC", "pH_T_insitu"]

mlr_carb_data = (
    carb_counts_unit[cols].where(carb_counts_unit[cols] > 0).count()
)

print(f"\nnumber of units with carb data :\n{mlr_carb_data}")

mlr_50min = carb_counts_unit[cols].where(carb_counts_unit[cols] >= 50).count()

print(f"\nnumber of units with count >= 50 :\n{mlr_50min}")

# %% Internal consistency statistics

carbclean = nwes.loc[
    (nwes.DIC.notnull())
    & (nwes.TA.notnull())
    & (nwes.pH_T_insitu.notnull())
    & (nwes.DIC_QC == 0)
    & (nwes.TA_QC == 0)
    & (nwes.pH_T_insitu_QC == 0)
    & (nwes.DIC_QCU_flag != "X")
    & (nwes.TA_QCU_flag != "X")
    & (nwes.pH_T_insitu_QCU_flag != "X")
]

print(
    f"\nnumber of datapoints with QC=0 and QCU_flag = C or W:\n{len(carbclean)}"
)

# %% Calculate carb params to do statistics on the internal consistency

# create nutrient columns for carbonate system calculations with 0 when no value
carbclean["Silicate_calc"] = np.where(
    carbclean["Silicate"].isnull(),
    0,
    carbclean["Silicate"],
)

carbclean["Phosphate_calc"] = np.where(
    carbclean["Phosphate"].isnull(),
    0,
    carbclean["Phosphate"],
)

carbclean["Ammonium_calc"] = np.where(
    carbclean["Ammonium"].isnull(),
    0,
    carbclean["Ammonium"],
)


carbclean["TA_calculated"] = pyco2.sys(
    par1=carbclean.DIC,
    par1_type=2,
    par2=carbclean.pH_T_insitu,
    par2_type=3,
    salinity=carbclean.CTDSAL,
    temperature=carbclean.CTDTEMP,
    pressure=carbclean.CTDPRES,
    total_silicate=carbclean.Silicate_calc,
    total_phosphate=carbclean.Phosphate_calc,
    total_ammonia=carbclean.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["alkalinity"]

carbclean["DIC_calculated"] = pyco2.sys(
    par1=carbclean.TA,
    par1_type=1,
    par2=carbclean.pH_T_insitu,
    par2_type=3,
    salinity=carbclean.CTDSAL,
    temperature=carbclean.CTDTEMP,
    pressure=carbclean.CTDPRES,
    total_silicate=carbclean.Silicate_calc,
    total_phosphate=carbclean.Phosphate_calc,
    total_ammonia=carbclean.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["dic"]

carbclean["pH_T_insitu_calculated"] = pyco2.sys(
    par1=carbclean.DIC,
    par1_type=2,
    par2=carbclean.TA,
    par2_type=1,
    salinity=carbclean.CTDSAL,
    temperature=carbclean.CTDTEMP,
    pressure=carbclean.CTDPRES,
    total_silicate=carbclean.Silicate_calc,
    total_phosphate=carbclean.Phosphate_calc,
    total_ammonia=carbclean.Ammonium_calc,
    **pyco2_kwargs,
    opt_pH_scale=1,  # for total scale
)["pH_total"]


# Create new columns with difference between calculated and measured values
carbclean["TA_diff"] = carbclean.TA_calculated - carbclean.TA
carbclean["DIC_diff"] = carbclean.DIC_calculated - carbclean.DIC
carbclean["pH_T_insitu_diff"] = (
    carbclean.pH_T_insitu_calculated - carbclean.pH_T_insitu
)

# %% Weather quality goal met for internal consistency

TA10 = carbclean.loc[(carbclean.TA_diff <= 10) & (carbclean.TA_diff >= -10)]
print(f"\nPercentage TA within 10 µmol kg-1:\n{len(TA10)*100/len(carbclean)}")

DIC10 = carbclean.loc[
    (carbclean.DIC_diff <= 10) & (carbclean.DIC_diff >= -10)
]
print(
    f"\nPercentage DIC within 10 µmol kg-1:\n{len(DIC10)*100/len(carbclean)}"
)

pH002 = carbclean.loc[
    (carbclean.pH_T_insitu_diff <= 0.02)
    & (carbclean.pH_T_insitu_diff >= -0.02)
]
print(
    f"\nPercentage pH_T_insitu within 0.02:\n{len(pH002)*100/len(carbclean)}"
)

# %% Climate quality goal met for internal consistency

TA2 = carbclean.loc[(carbclean.TA_diff <= 2) & (carbclean.TA_diff >= -2)]
print(f"\nPercentage TA within 2 µmol kg-1:\n{len(TA2)*100/len(carbclean)}")

DIC2 = carbclean.loc[(carbclean.DIC_diff <= 2) & (carbclean.DIC_diff >= -2)]
print(f"\nPercentage DIC within 2 µmol kg-1:\n{len(DIC2)*100/len(carbclean)}")

pH0003 = carbclean.loc[
    (carbclean.pH_T_insitu_diff <= 0.003)
    & (carbclean.pH_T_insitu_diff >= -0.003)
]
print(
    f"\nPercentage pH_T_insitu within 0.003:\n{len(pH0003)*100/len(carbclean)}"
)

# %% Number of datapoints with one, two or three carbonate system variables

cols = ["TA", "DIC", "pH_T_insitu"]

# Count how many non-NaN values each row has across A, B, C
non_nan_per_row = nwes[cols].notna().sum(axis=1)

# Count rows by category
count_one = (non_nan_per_row == 1).sum()
count_two = (non_nan_per_row == 2).sum()
count_three = (non_nan_per_row == 3).sum()

print(f"\nRows with 1 carb parameter: {count_one}")
print(f"\nRows with 2 carb parameter: {count_two}")
print(f"\nRows with 3 carb parameter: {count_three}")


print(f"\nRows with 1 carb parameter in %: {(count_one)*100/len(nwes)}")
print(f"\nRows with 2 carb parameter in %: {(count_two)*100/len(nwes)}")
print(f"\nRows with 3 carb parameter in %: {(count_three)*100/len(nwes)}")


# %% Number of datapoints per variable

cols = [
    "CTDTEMP",
    "CTDSAL",
    "TA",
    "DIC",
    "pH_T_insitu",
    "CTDOXY",
    "Oxygen",
    "Nitrate",
    "Nitrite",
    "Ammonium",
    "Silicate",
    "Phosphate",
]
nwes[cols].count()

# %% Temporal distribution data

# Split data into before 2000 and from 2000 onwards
cutoff_date = 2000

before_2000 = nwes[nwes.Year_UTC < cutoff_date]
from_2000 = nwes[nwes.Year_UTC >= cutoff_date]

count_before = len(before_2000)
count_from = len(from_2000)

pct_before = (count_before / len(nwes)) * 100
pct_from = (count_from / len(nwes)) * 100

print(f"Before {cutoff_date}:      {count_before} ({pct_before:.2f}%)")
print(f"From {cutoff_date}:        {count_from} ({pct_from:.2f}%)")

TA_only = nwes.loc[nwes.TA.notnull()]
before_2000_TA = TA_only[TA_only.Year_UTC < cutoff_date]
from_2000_TA = TA_only[TA_only.Year_UTC >= cutoff_date]
count_before_TA = len(before_2000_TA)
count_from_TA = len(from_2000_TA)
pct_before_TA = (count_before_TA / len(TA_only)) * 100
pct_from_TA = (count_from_TA / len(TA_only)) * 100
print(
    f"Before {cutoff_date} for TA:      {count_before_TA} ({pct_before_TA:.2f}%)"
)
print(
    f"From {cutoff_date} for TA:        {count_from_TA} ({pct_from_TA:.2f}%)"
)

DIC_only = nwes.loc[nwes.DIC.notnull()]
before_2000_DIC = DIC_only[DIC_only.Year_UTC < cutoff_date]
from_2000_DIC = DIC_only[DIC_only.Year_UTC >= cutoff_date]
count_before_DIC = len(before_2000_DIC)
count_from_DIC = len(from_2000_DIC)
pct_before_DIC = (count_before_DIC / len(DIC_only)) * 100
pct_from_DIC = (count_from_DIC / len(DIC_only)) * 100
print(
    f"Before {cutoff_date} for DIC:      {count_before_DIC} ({pct_before_DIC:.2f}%)"
)
print(
    f"From {cutoff_date} for DIC:        {count_from_DIC} ({pct_from_DIC:.2f}%)"
)

pH_only = nwes.loc[nwes.pH_T_insitu.notnull()]
before_2000_pH = pH_only[pH_only.Year_UTC < cutoff_date]
from_2000_pH = pH_only[pH_only.Year_UTC >= cutoff_date]
count_before_pH = len(before_2000_pH)
count_from_pH = len(from_2000_pH)
pct_before_pH = (count_before_pH / len(pH_only)) * 100
pct_from_pH = (count_from_pH / len(pH_only)) * 100
print(
    f"Before {cutoff_date} for pH:      {count_before_pH} ({pct_before_pH:.2f}%)"
)
print(
    f"From {cutoff_date} for pH:        {count_from_pH} ({pct_from_pH:.2f}%)"
)

# %% Monthly and seasonal distribution

carb_counts_month = nwes.groupby(["Month_UTC"])[
    ["CTDTEMP", "TA", "DIC", "pH_T_insitu"]
].count()
print(f"\nmonthly distribution of carb params:\n{carb_counts_month}")

carb_percent_month = (
    carb_counts_month.div(carb_counts_month.sum(), axis=1)
    .mul(100)
    .round(1)
    .rename(columns=lambda c: f"%{c}")
)

print(f"\nmonthly distribution of carb params in %:\n{carb_percent_month}")

carb_counts_year = nwes.groupby(["Year_UTC"])[
    ["CTDTEMP", "TA", "DIC", "pH_T_insitu"]
].count()
print(f"\nyearly distribution of carb params:\n{carb_counts_year}")


carb_percent_year = (
    carb_counts_year.div(carb_counts_year.sum(), axis=1)
    .mul(100)
    .round(1)
    .rename(columns=lambda c: f"%{c}")
)

print(f"\nyearly distribution of carb params in %:\n{carb_percent_year}")

nwes["season"] = np.nan
nwes["season"] = np.where(
    ((nwes.Datetime.dt.month > 2) & (nwes.Datetime.dt.month < 6)),
    "spring",
    nwes["season"],
)

nwes["season"] = np.where(
    ((nwes.Datetime.dt.month > 5) & (nwes.Datetime.dt.month < 9)),
    "summer",
    nwes["season"],
)

nwes["season"] = np.where(
    ((nwes.Datetime.dt.month > 8) & (nwes.Datetime.dt.month < 12)),
    "autumn",
    nwes["season"],
)

nwes["season"] = np.where(
    (~((nwes.Datetime.dt.month > 2) & (nwes.Datetime.dt.month < 12))),
    "winter",
    nwes["season"],
)

carb_counts_season = nwes.groupby(["season"])[
    ["CTDTEMP", "TA", "DIC", "pH_T_insitu"]
].count()

print(f"\nseasonal distribution of carb params:\n{carb_counts_season}")

carb_percent_season = (
    carb_counts_season.div(carb_counts_season.sum(), axis=1)
    .mul(100)
    .round(1)
    .rename(columns=lambda c: f"%{c}")
)

print(f"\nseasonal distribution of carb params in %:\n{carb_percent_season}")

# %% Depth distribution
# minimum depth per unit
depth_min = (
    nwes.groupby(
        ["Name_ID"],
    )["Depth"]
    .min()
    .rename("depth_min")
)
# maximum depth per unit
depth_max = (
    nwes.groupby(
        ["Name_ID"],
    )["Depth"]
    .max()
    .rename("depth_max")
)
# range of depth per unit
range_depth = (depth_max - depth_min).rename("range_depth")

# create dataframe with all information
stats = pd.concat([depth_min, depth_max, range_depth], axis=1)


surface_only = stats.loc[stats.depth_max <= 10]
print(
    f"\nNumber of units only with surface data (<=10m) is {len(surface_only)}/{len(stats)} = {len(surface_only)*100/len(stats)} "
)

print(
    f"\nNumber of surface datapoints (<=10m) in entire dataset is {len(nwes.loc[nwes.Depth <= 10])}/{len(nwes)} = {len(nwes.loc[nwes.Depth <= 10])*100/len(nwes)} "
)


# %% Number of stations

lon_sum = (
    nwes.groupby(
        ["Name_ID"],
    )["Longitude"]
    .nunique()
    .rename("lon_sum")
)

lat_sum = (
    nwes.groupby(
        ["Name_ID"],
    )["Latitude"]
    .nunique()
    .rename("lat_sum")
)

stats = pd.concat([stats, lon_sum, lat_sum], axis=1)

unique_station = stats.loc[(stats.lon_sum == 1) & (stats.lat_sum == 1)]

print(
    f"\nNumber of units with only one station is {len(unique_station)}/{len(stats)} = {len(unique_station)*100/len(stats)} "
)


n_stations = nwes[["Longitude", "Latitude"]].drop_duplicates().shape[0]

print(
    f"\nNumber of unique stations: {n_stations} (but some are same stations with a small location difference)"
)

# %% Number of stations rounded 2 decimals

nwes["longitude_2dec"] = nwes.Longitude.round(decimals=2)
nwes["latitude_2dec"] = nwes.Latitude.round(decimals=2)

lon_2dec_sum = (
    nwes.groupby(
        ["Name_ID"],
    )["longitude_2dec"]
    .nunique()
    .rename("lon_2dec_sum")
)

lat_2dec_sum = (
    nwes.groupby(
        ["Name_ID"],
    )["latitude_2dec"]
    .nunique()
    .rename("lat_2dec_sum")
)

stats_2dec = pd.concat([stats, lon_2dec_sum, lat_2dec_sum], axis=1)

unique_station_2dec = stats_2dec.loc[
    (stats_2dec.lon_2dec_sum == 1) & (stats_2dec.lat_2dec_sum == 1)
]

print(
    f"\nNumber of units with only one station is {len(unique_station_2dec)}/{len(stats_2dec)} = {len(unique_station_2dec)*100/len(stats_2dec)} "
)

n_stations_2dec = (
    nwes[["longitude_2dec", "latitude_2dec"]].drop_duplicates().shape[0]
)

print(
    f"\nNumber of unique stations: {n_stations_2dec} (rounded at 2 decimals)"
)
