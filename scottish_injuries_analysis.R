# Scottish Unintentional Injuries Analysis (R)
#
# Question 1: Across Scotland, what are the most and least common
# unintentional injuries for young people aged 5-14 in 2013/14 and 2022/23,
# and did admission rates change between the two periods?
#
# Data: Public Health Scotland "Unintentional Injuries" open dataset,
# joined with the NHS Scotland health board reference table.

library(tidyverse)
library(lubridate)
library(rjson)
library(ggplot2)
library(forcats)

# ---- Load data ---------------------------------------------------------

injuries <- read_csv("data/scot_unintentional_injuries.csv")
healthboards <- read_csv("data/healthboards.csv")

# ---- Join and type-cast -------------------------------------------------

joined_df <- left_join(injuries, healthboards, by = c("HBR" = "HB"))

correct_type <- joined_df %>%
  mutate(
    FinancialYear = as.factor(FinancialYear),
    AgeGroup = as.factor(AgeGroup),
    InjuryType = as.factor(InjuryType),
    NumberOfAdmissions = as.integer(NumberOfAdmissions),
    HBR = as.factor(HBR),
    CountryName = as.factor(CountryName)
  )

# ---- Filter to the population and years of interest ---------------------

minimised_df <- correct_type %>%
  select(FinancialYear, HBR, AgeGroup, InjuryType, NumberOfAdmissions, CountryName) %>%
  filter(
    CountryName == "Scotland",
    AgeGroup %in% c("5-9 years", "10-14 years"),
    FinancialYear %in% c("2013/14", "2022/23")
  )

# ---- Standardise inconsistent injury-type labels -------------------------

cleaned <- minimised_df %>%
  mutate(InjuryType = fct_recode(InjuryType,
    "Falls" = "Falling",
    "Poisoning" = "Poisoned",
    "Scalds" = "Scalded",
    "Collision-related" = "Struck by, against",
    "Collision-related" = "RTA",
    "Collision-related" = "Crushing"
  ))

# ---- Summarise and plot --------------------------------------------------

cleaned %>%
  group_by(FinancialYear, InjuryType) %>%
  summarise(Admissions = sum(NumberOfAdmissions, na.rm = TRUE), .groups = "drop") %>%
  ggplot(aes(x = reorder(InjuryType, Admissions), y = Admissions, fill = FinancialYear)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Injury Admissions for Ages 5-14 in 2013/14 and 2022/23",
    x = "Injury Type",
    y = "Number of Admissions"
  ) +
  theme_minimal()

# Finding: "Falls" was the most common cause of admission in both years;
# "Scalds" and "Poisoning" were the least common. Falls admissions fell
# slightly over the period while some other categories increased.


# =====================================================================
# Question 2: Reconstructing a semi-structured JSON medication dataset
# Some records are missing a field at an unpredictable position, which
# misaligns a naive row-bind. Rows are split into complete vs. short,
# the short ones are padded back to 10 fields at known positions, then
# both sets are recombined and given correct column types.
# =====================================================================

medications <- fromJSON(file = "data/task2_data.json")

# Split into complete (10-field) rows and short/scrambled rows
medications_clean_list <- medications[lengths(medications) == 10]
medications_scrambled_list <- medications[lengths(medications) != 10]

medications_clean_tibble <- as_tibble(
  do.call(rbind, medications_clean_list),
  .name_repair = "minimal"
)
colnames(medications_clean_tibble) <- c(
  "BNF_Code", "PrescriptionDate", "Source", "Dose", "Unit",
  "Colour", "Shape", "Age", "FridgeFlag", "Frequency"
)

# Inspect the scrambled rows to find which field index is missing in each
medications_scrambled_list[]

# Known missing-field position for each scrambled row (1-based), found by
# inspection above. Pad each row with NA at that position.
positions <- c(5, 8, 5, 6, 8, 5, 5, 5)
values_to_insert <- rep(list(NA), length(positions))

for (i in seq_along(medications_scrambled_list)) {
  medications_scrambled_list[[i]] <- medications_scrambled_list[[i]] %>%
    append(values_to_insert[[i]], after = positions[i] - 1)
}

medications_corrected_tibble <- as_tibble(
  do.call(rbind, medications_scrambled_list),
  .name_repair = "minimal"
)
colnames(medications_corrected_tibble) <- c(
  "BNF_Code", "PrescriptionDate", "Source", "Dose", "Unit",
  "Colour", "Shape", "Age", "FridgeFlag", "Frequency"
)

# Combine, drop columns not needed downstream, and assign correct types
df_selected <- bind_rows(medications_clean_tibble, medications_corrected_tibble) %>%
  select(-Colour, -Shape, -Age) %>%
  mutate(
    PrescriptionDate = dmy(PrescriptionDate),
    Dose = as.numeric(Dose),
    Unit = as.factor(Unit),
    Frequency = as.integer(str_remove(Frequency, "x")),
    Source = str_to_lower(Source),
    Source = case_when(
      Source %in% c("hosp", "hopsital", "hospital") ~ "hospital",
      Source %in% c("pharm", "pharmacy") ~ "pharmacy",
      Source %in% c("dent", "dentist") ~ "dentist",
      TRUE ~ Source
    ),
    Source = factor(Source),
    FridgeFlag = as.logical(as.integer(FridgeFlag))
  )

glimpse(df_selected)
