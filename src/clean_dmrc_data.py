import numpy as np
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "dmrc_fare_prediction_raw.csv"
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "cleaned" / "dmrc_fare_prediction_cleaned.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"

EXPECTED_COLUMNS = [
    "Trip_ID",
    "Origin_Station",
    "Destination_Station",
    "Corridor_Line",
    "Travel_Distance_km",
    "Interchange_Count",
    "Is_Airport_Express",
    "Is_Peak_Hour",
    "Ticket_Type",
    "Ticket_Fare_INR",
]
TEXT_COLUMNS = [
    "Trip_ID",
    "Origin_Station",
    "Destination_Station",
    "Corridor_Line",
    "Ticket_Type",
]
NUMERIC_COLUMNS = [
    "Travel_Distance_km",
    "Interchange_Count",
    "Is_Airport_Express",
    "Is_Peak_Hour",
    "Ticket_Fare_INR",
]
FLAG_COLUMNS = ["Is_Airport_Express", "Is_Peak_Hour"]
MISSING_MARKERS = {"", "??", "n/a", "na", "unknown", "nan", "null"}


if not RAW_DATA_PATH.exists():
    raise FileNotFoundError(f"Raw dataset was not found: {RAW_DATA_PATH}")

# Keep values as text first so whitespace and missing markers can be handled consistently.
raw_df = pd.read_csv(RAW_DATA_PATH, dtype=str, keep_default_na=False)

if set(raw_df.columns) != set(EXPECTED_COLUMNS):
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(raw_df.columns))
    extra_columns = sorted(set(raw_df.columns) - set(EXPECTED_COLUMNS))
    raise ValueError(
        f"Unexpected CSV columns. Missing: {missing_columns}; extra: {extra_columns}"
    )

source_row_count = len(raw_df)
exact_duplicate_rows = int(raw_df.duplicated().sum())

df = raw_df[EXPECTED_COLUMNS].copy()

# Trim text and convert common placeholder values to missing values.
trimmed_values = {}
for column in EXPECTED_COLUMNS:
    original_values = df[column]
    values = original_values.str.strip()
    trimmed_values[column] = int(original_values.ne(values).sum())
    is_missing = values.str.casefold().isin(MISSING_MARKERS)
    df[column] = values.mask(is_missing, np.nan)

missing_values = df.isna().sum()
repeated_trip_id_rows = int(df["Trip_ID"].duplicated(keep="first").sum())

invalid_numeric_values = {}
for column in NUMERIC_COLUMNS:
    original_values = df[column]
    numeric_values = pd.to_numeric(original_values, errors="coerce")
    invalid_numeric_values[column] = int(
        (original_values.notna() & numeric_values.isna()).sum()
    )
    df[column] = numeric_values

# Keep complete rows with valid numbers, non-negative counts, and 0/1 flags.
finite_numbers = pd.Series(
    np.isfinite(df[NUMERIC_COLUMNS]).all(axis=1),
    index=df.index,
)
valid_flags = df[FLAG_COLUMNS].isin([0, 1]).all(axis=1)
valid_interchanges = (
    df["Interchange_Count"].ge(0)
    & df["Interchange_Count"].mod(1).eq(0)
)
valid_distance_and_fare = (
    df["Travel_Distance_km"].gt(0)
    & df["Ticket_Fare_INR"].ge(0)
)
complete_text = df[TEXT_COLUMNS].notna().all(axis=1)

valid_rows = (
    df[EXPECTED_COLUMNS].notna().all(axis=1)
    & complete_text
    & finite_numbers
    & valid_flags
    & valid_interchanges
    & valid_distance_and_fare
)
valid_df = df.loc[valid_rows].copy()
if valid_df.empty:
    raise ValueError("No complete, valid trip records were found in the raw dataset.")

# Do not choose arbitrarily if valid duplicates for one trip disagree.
duplicate_rows = valid_df[valid_df.duplicated("Trip_ID", keep=False)]
conflicting_ids = (
    duplicate_rows.groupby("Trip_ID")[EXPECTED_COLUMNS]
    .nunique(dropna=False)
    .gt(1)
    .any(axis=1)
)
if conflicting_ids.any():
    examples = ", ".join(conflicting_ids[conflicting_ids].index[:5])
    raise ValueError(f"Conflicting valid rows found for Trip_ID values: {examples}")

cleaned_df = (
    valid_df.drop_duplicates(subset="Trip_ID", keep="first")
    .sort_values("Trip_ID")
    .reset_index(drop=True)
)

for column in ["Interchange_Count"] + FLAG_COLUMNS:
    cleaned_df[column] = cleaned_df[column].astype(int)

cleaned_df = cleaned_df[EXPECTED_COLUMNS]

summary_rows = [
    ("Source file", str(RAW_DATA_PATH.relative_to(PROJECT_ROOT))),
    ("Source rows", source_row_count),
    ("Source columns", len(raw_df.columns)),
    ("Exact duplicate source rows", exact_duplicate_rows),
    ("Repeated Trip_ID rows in source", repeated_trip_id_rows),
    (
        "Rows with invalid indicator flags",
        int((~df[FLAG_COLUMNS].isin([0, 1]).all(axis=1)).sum()),
    ),
    ("Rows removed for missing or invalid values", source_row_count - len(valid_df)),
    ("Valid rows before Trip_ID deduplication", len(valid_df)),
    ("Repeated valid Trip_ID rows removed", len(valid_df) - len(cleaned_df)),
    ("Cleaned rows", len(cleaned_df)),
]
summary_rows.extend(
    (f"Missing values in {column}", int(count))
    for column, count in missing_values.items()
)
summary_rows.extend(
    (
        (f"Missing percentage in {column}", round(count / source_row_count * 100, 2))
        for column, count in missing_values.items()
    )
)
summary_rows.extend(
    (f"Values trimmed in {column}", count)
    for column, count in trimmed_values.items()
)
summary_rows.extend(
    (f"Non-numeric values in {column}", count)
    for column, count in invalid_numeric_values.items()
)

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
cleaned_df.to_csv(CLEANED_DATA_PATH, index=False)
pd.DataFrame(summary_rows, columns=["Measure", "Value"]).to_csv(
    REPORTS_DIR / "data_cleaning_summary.csv",
    index=False,
)

print(f"Source rows: {source_row_count}")
print(f"Rows removed for missing or invalid values: {source_row_count - len(valid_df)}")
print(f"Repeated valid Trip_ID rows removed: {len(valid_df) - len(cleaned_df)}")
print(f"Cleaned rows: {len(cleaned_df)}")
print(f"Saved cleaned data to {CLEANED_DATA_PATH}")
print(f"Saved cleaning summary to {REPORTS_DIR / 'data_cleaning_summary.csv'}")
