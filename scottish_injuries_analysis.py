"""
Scottish Unintentional Injuries Analysis (Python)

Question 1: Among people aged 65+ in NHS Lothian and NHS Greater Glasgow and
Clyde, what were the four most common causes of unintentional-injury
hospital admissions in 2020/21, and how did the two health boards compare?

Data: Public Health Scotland "Unintentional Injuries" open dataset, joined
with the NHS Scotland health board reference table.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

# ---- Load and merge ------------------------------------------------------

injuries = pd.read_csv("data/scot_unintentional_injuries.csv")
healthboards = pd.read_csv("data/healthboards.csv")

merged_data = injuries.merge(healthboards, left_on="HBR", right_on="HB", how="left")
merged_data["NumberOfAdmissions"] = pd.to_numeric(merged_data["NumberOfAdmissions"], errors="coerce")
merged_data["FinancialYear"] = merged_data["FinancialYear"].astype("category")
merged_data["InjuryType"] = merged_data["InjuryType"].astype("category")
merged_data["AgeGroup"] = merged_data["AgeGroup"].astype("category")
merged_data["HBName"] = merged_data["HBName"].astype("category")

# ---- Filter to the population and boards of interest ---------------------

subset = merged_data[
    (merged_data["AgeGroup"].isin(["65-74 years", "75plus years"]))
    & (merged_data["FinancialYear"] == "2020/21")
    & (merged_data["HBName"].isin(["NHS Lothian", "NHS Greater Glasgow and Clyde"]))
].copy()

assert "NHS Lothian" in merged_data["HBName"].values
assert "NHS Greater Glasgow and Clyde" in merged_data["HBName"].values

# ---- Standardise inconsistent injury-type labels --------------------------

subset["InjuryType"] = (
    subset["InjuryType"]
    .str.strip()
    .str.lower()
    .str.title()
    .replace(
        {
            "Falling": "Falls",
            "Falling ": "Falls",
            "Poisoned": "Poisoning",
            "Poisoned ": "Poisoning",
            "Scalded": "Scalds",
            "Rta": "Collision-Related",
            "Struck By, Against": "Collision-Related",
            "Crushing": "Collision-Related",
            "Other ": "Other",
            "other": "Other",
            "other ": "Other",
        }
    )
)
subset["InjuryType"] = subset["InjuryType"].astype("category")

# ---- Group, rank, and plot the top 4 causes per board ---------------------

grouped = (
    subset.groupby(["HBName", "InjuryType"], observed=True)["NumberOfAdmissions"]
    .sum()
    .reset_index()
)

top4 = (
    grouped.sort_values("NumberOfAdmissions", ascending=False)
    .groupby("HBName")
    .head(4)
)

plt.figure(figsize=(8, 5))
sns.barplot(data=top4, x="NumberOfAdmissions", y="InjuryType", hue="HBName")
plt.title("Top 4 Causes of Injury Admissions (65+, 2020/21)")
plt.xlabel("Number of Admissions")
plt.ylabel("Injury Type")
plt.legend(title="Health Board")
plt.tight_layout()
plt.show()

# Finding: the two boards shared three of their top four causes
# (Falls, Accidental Exposure, Other), differing in the fourth:
# Collision-Related for NHS Lothian vs. Poisoning for NHS Greater
# Glasgow and Clyde.


# =====================================================================
# Question 2: Reconstructing a semi-structured JSON medication dataset
# Records are stored as unnamed lists of varying length because one
# field is missing (at an unpredictable position) in some rows. Rows
# are split into complete vs. short, the short ones are padded back to
# 10 fields at known positions, then both sets are combined into a
# typed DataFrame.
# =====================================================================


def load_json_file_named(file_name):
    """Load a JSON file from the data/ folder."""
    loaded_data = []
    file_location = f"data/{file_name}"
    try:
        with open(file_location, "r") as file:
            loaded_data = json.load(file)
    except OSError as e:
        print(f"Error. Does the file exist in this folder? {file_location}\n\n {e}")
    return loaded_data


medications = load_json_file_named("task2_data.json")

# Rows with all 10 fields (clean) vs. fewer fields (scrambled)
medications_clean = [row for row in medications if len(row) == 10]
medications_scrambled = [row for row in medications if len(row) != 10]

# Missing-field position for each scrambled row (1-based index), found by
# inspecting medications_scrambled above
insertion_positions = [5, 8, 5, 6, 8, 5, 5, 5]

corrected_rows = []
for row, pos in zip(medications_scrambled, insertion_positions):
    padded = row[: pos - 1] + [None] + row[pos - 1 :]
    corrected_rows.append(padded)

col_names = [
    "BNF_Code", "PrescriptionDate", "Source", "Dose", "Unit",
    "Colour", "Shape", "Age", "FridgeFlag", "Frequency",
]

all_rows = medications_clean + corrected_rows
df = pd.DataFrame(all_rows, columns=col_names)

df_cleaned = df.copy().assign(
    PrescriptionDate=pd.to_datetime(df["PrescriptionDate"], format="%d%m%Y", errors="coerce"),
    Dose=pd.to_numeric(df["Dose"], errors="coerce"),
)

df_final = df_cleaned.drop(columns=["Age", "Shape", "Colour"])
df_final = df_final.sort_values(by="PrescriptionDate")
df_final[["Source", "Unit"]] = df_final[["Source", "Unit"]].astype(
    {"Source": "category", "Unit": "category"}
)

print(df_final.info())
