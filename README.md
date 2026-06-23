# Scottish Unintentional Injuries Analysis

Dual R/Python analysis of NHS Scotland's open "Unintentional Injuries" dataset, plus a data-repair exercise on a deliberately malformed JSON medication dataset. PGDip Data Science (Health & Social Care) project.

## Problem

Two questions, answered independently in both R and Python:

1. **Injury trends by age and time** — Across Scotland, what are the most and least common unintentional injuries for children aged 5–14, and how did admission rates change between 2013/14 and 2022/23?
2. **Regional comparison** — Among adults aged 65+, what were the top four causes of injury admission in NHS Lothian vs. NHS Greater Glasgow and Clyde in 2020/21?

A separate, smaller exercise: reconstruct a usable table from a JSON file where some prescription records are missing a field at an unpredictable position.

## Data

- Public Health Scotland [Unintentional Injuries](https://www.opendata.nhs.scot/dataset/unintentional-injuries) open dataset
- NHS Scotland health board reference table (`healthboards.csv`)
- A synthetic, intentionally malformed JSON file of prescription records (`task2_data.json`), used as a controlled exercise in handling semi-structured/irregular data

Data files are not included in this repo (the injuries dataset is large and the JSON file was provided as part of a university assessment). Source: [opendata.nhs.scot](https://www.opendata.nhs.scot/dataset/unintentional-injuries).

## Method

- **Injury trends (R)** — join injuries to health boards, filter to ages 5–14 and the two financial years, standardise inconsistent injury-type labels (e.g. "Falling" / "Falling " → "Falls"), aggregate and plot with `ggplot2`.
- **Regional comparison (Python)** — same join/filter/clean pattern using `pandas`, ranked with `groupby` + `sort_values`, visualised with `seaborn`.
- **JSON repair (R + Python)** — split records into complete (10-field) and short rows, identify the missing-field position in each short row by inspection, pad with `NA`/`None` at that position, recombine, then cast to correct types (dates, numeric dose, categorical source/unit, boolean fridge flag).

## Results

- **Ages 5–14:** "Falls" was the most common cause of admission in both 2013/14 and 2022/23; "Scalds" and "Poisoning" were the least common. Falls admissions fell slightly over the period while some other categories rose.
- **Ages 65+:** NHS Lothian and NHS Greater Glasgow and Clyde shared three of their top four injury causes (Falls, Accidental Exposure, Other), differing in the fourth — Collision-related for Lothian, Poisoning for Greater Glasgow and Clyde.
- **JSON repair:** all malformed records were successfully realigned into a single typed table with no data loss.

## Known issues / limitations

- The missing-field positions for the malformed JSON rows were identified by manual inspection rather than programmatically detected — fine for a fixed, known dataset, but not robust to a differently-shaped corruption pattern.
- Injury-type label cleanup uses a hand-built lookup table; a larger or shifting set of raw labels would need a more general matching approach (e.g. fuzzy matching).

## Skills demonstrated

- Data cleaning and type coercion in both R (`dplyr`, `forcats`) and Python (`pandas`)
- Joining and filtering relational health datasets
- Recovering structure from semi-structured/malformed data (JSON with inconsistent record lengths)
- Categorical data standardisation across inconsistent text labels
- Comparative visualisation (`ggplot2`, `seaborn`)
- Parallel implementation of the same analysis in two languages

## Files

- `scottish_injuries_analysis.R` — Task 1 (age/time trends) and Task 2 (JSON repair) in R
- `scottish_injuries_analysis.py` — Task 1 (regional comparison) and Task 2 (JSON repair) in Python
# scottish-unintentional-injuries-analysis
Scottish unintentional injury admissions by age, year, and health board, plus a semi-structured JSON data-repair exercise. R and Python, dual implementation. PGDip Data Science project.
