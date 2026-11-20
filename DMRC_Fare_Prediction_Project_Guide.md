# DMRC Fare Prediction Project

This project looks at Delhi Metro trip data and makes a simple fare estimate.
It is a student project for learning data analysis with Python.

The code uses only **pandas** and **NumPy**. It does not use a machine-learning
package. The fare estimate is an average from similar trips, so it should not
be treated as an official DMRC fare or a trained model.

## Project folders

```text
data/
  raw/
    dmrc_fare_prediction_raw.csv
  cleaned/
    dmrc_fare_prediction_cleaned.csv
  processed/
    dmrc_fare_results.csv
docs/
  requirements/
    DMRC_Data_Cleaning_SRS_Numpy_Pandas.docx
    DMRC_Fare_Prediction_SRS.docx
reports/
  archive/                      # Reports from an earlier model experiment
  data_cleaning_summary.csv     # Created by the cleaning script
  line_summary.csv             # Created by the analysis script
src/
  clean_dmrc_data.py
  dmrc_fare_prediction.py
requirements.txt
DMRC_Fare_Prediction_Project_Guide.md
```

The raw file is kept unchanged. The cleaning script creates the cleaned file;
the fare analysis script reads that cleaned file.

## Install the required packages

Open a terminal in the project folder and run:

```powershell
python -m pip install -r requirements.txt
```

## Run the project

First, clean the raw data:

```powershell
python src/clean_dmrc_data.py
```

Then run the fare analysis:

```powershell
python src/dmrc_fare_prediction.py
```

The raw CSV has 12,450 rows. The cleaning script trims extra spaces, treats
common placeholder values as missing, checks numeric fields and flags, removes
incomplete or invalid rows, and removes repeated trip IDs when their valid
records agree. If valid rows for one trip disagree, the script stops and shows
the conflicting trip IDs instead of choosing one silently. For the supplied
file, this produces 6,000 cleaned trips.

The analysis script shows basic information about the trips, compares fares,
and estimates fares by averaging trips with a similar distance range, ticket
type, peak-hour value, and airport-express value.

The average difference printed by the analysis is measured on the same trips
used to calculate those averages. It is not a test of how well estimates work
for new trips.

## Output files

- `data/cleaned/dmrc_fare_prediction_cleaned.csv` contains the cleaned trips.
- `data/processed/dmrc_fare_results.csv` contains the trips and fare estimates.
- `reports/data_cleaning_summary.csv` records the cleaning counts.
- `reports/line_summary.csv` summarizes trips and fares by metro line.
- `reports/archive/` keeps older reports that the current scripts do not create.

The two SRS documents are in `docs/requirements/`. They were supplied for this
project. They describe broader requirements; the current scripts implement a
basic data-cleaning and fare-analysis workflow, not every requirement in the
SRS documents.

## Project made by

- **Name:** Adirya Kumar Maurya
- **Program:** B.TECH 1st year CSE 2
- **Admission number:** 2026B01010410
- **Email:** [aditya26b01010410@abes.ac.in](mailto:aditya26b01010410@abes.ac.in)