import numpy as np
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "dmrc_fare_prediction_cleaned.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 1. reading the data ----------
df = pd.read_csv(DATA_PATH)

print("First 5 rows")
print(df.head())

print("\nShape (rows, columns):", df.shape)
print("\nColumn info")
df.info()

print("\nMissing values in each column")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

# ---------- 2. basic statistics ----------
print("\nBasic statistics")
print(df.describe())

fares = df["Ticket_Fare_INR"].to_numpy()
print("\nUsing numpy on the fare column")
print("Average fare :", np.mean(fares).round(2))
print("Median fare  :", np.median(fares))
print("Minimum fare :", np.min(fares))
print("Maximum fare :", np.max(fares))
print("Std deviation:", np.std(fares).round(2))

# ---------- 3. checking the categories ----------
print("\nTrips on each line")
print(df["Corridor_Line"].value_counts())

print("\nTrips by ticket type")
print(df["Ticket_Type"].value_counts())

# ---------- 4. how fare changes with different things ----------
print("\nAverage fare by ticket type")
print(df.groupby("Ticket_Type")["Ticket_Fare_INR"].mean().round(2))

print("\nAverage fare - peak hour (1) vs non peak (0)")
print(df.groupby("Is_Peak_Hour")["Ticket_Fare_INR"].mean().round(2))

print("\nAverage fare - airport express (1) vs normal (0)")
print(df.groupby("Is_Airport_Express")["Ticket_Fare_INR"].mean().round(2))

print("\nAverage fare by number of interchanges")
print(df.groupby("Interchange_Count")["Ticket_Fare_INR"].mean().round(2))

print("\nAverage distance and fare for each line")
line_summary = df.groupby("Corridor_Line").agg(
    trips=("Trip_ID", "count"),
    avg_distance=("Travel_Distance_km", "mean"),
    avg_fare=("Ticket_Fare_INR", "mean"),
)
print(line_summary.round(2).sort_values("avg_fare", ascending=False))

# ---------- 5. distance vs fare ----------
# correlation tells how strongly two columns move together
print("\nCorrelation of fare with other columns")
number_cols = ["Travel_Distance_km", "Interchange_Count",
               "Is_Airport_Express", "Is_Peak_Hour", "Ticket_Fare_INR"]
print(df[number_cols].corr()["Ticket_Fare_INR"].round(3))

# grouping the distance into ranges
df["Distance_Range"] = pd.cut(
    df["Travel_Distance_km"],
    bins=[0, 5, 12, 21, 32, 60],
    labels=["0-5 km", "5-12 km", "12-21 km", "21-32 km", "32+ km"],
)
print("\nAverage fare for each distance range")
print(df.groupby("Distance_Range", observed=True)["Ticket_Fare_INR"].mean().round(2))

# ---------- 6. busiest routes ----------
print("\nTop 10 busiest routes")
routes = df.groupby(["Origin_Station", "Destination_Station"]).size()
print(routes.sort_values(ascending=False).head(10))

print("\nMost used origin stations")
print(df["Origin_Station"].value_counts().head(5))

print("\nMost used destination stations")
print(df["Destination_Station"].value_counts().head(5))

# ---------- 7. simple fare estimate ----------
# Idea: trips that look alike should cost about the same.
# So for every trip we take the average fare of all trips with the same
# distance range, ticket type, peak hour and airport express value.
group_cols = ["Distance_Range", "Ticket_Type", "Is_Peak_Hour", "Is_Airport_Express"]

fare_table = df.groupby(group_cols, observed=True)["Ticket_Fare_INR"].mean()
print("\nFirst few rows of the average fare table")
print(fare_table.round(2).head(10))

# estimated fare for every trip in the data
df["Estimated_Fare"] = df.groupby(group_cols, observed=True)["Ticket_Fare_INR"].transform("mean").round(2)

# how far is our estimate from the real fare
df["Difference"] = (df["Ticket_Fare_INR"] - df["Estimated_Fare"]).round(2)
print("\nAverage difference between real and estimated fare:",
      np.abs(df["Difference"]).mean().round(2), "rupees")

# comparing with a very basic estimate (one single rate per km for everyone)
overall_rate = np.sum(fares) / df["Travel_Distance_km"].sum()
basic_estimate = df["Travel_Distance_km"] * overall_rate
print("Average difference with one single rate per km     :",
      np.abs(df["Ticket_Fare_INR"] - basic_estimate).mean().round(2), "rupees")


# a small function to estimate the fare of a new trip
def estimate_fare(distance_km, ticket_type, peak_hour, airport=0):
    if distance_km <= 5:
        dist_range = "0-5 km"
    elif distance_km <= 12:
        dist_range = "5-12 km"
    elif distance_km <= 21:
        dist_range = "12-21 km"
    elif distance_km <= 32:
        dist_range = "21-32 km"
    else:
        dist_range = "32+ km"

    key = (dist_range, ticket_type, peak_hour, airport)
    if key in fare_table.index:
        return round(fare_table[key], 2)
    return None   # no similar trip in the data


print("\nExample estimates")
print("10 km, Smart Card, non peak  :", estimate_fare(10, "Smart Card", 0))
print("25 km, Token, peak           :", estimate_fare(25, "Token", 1))
print("40 km, QR Mobile Ticket, peak:", estimate_fare(40, "QR Mobile Ticket", 1))

# ---------- 8. final findings ----------
print("\nFINDINGS")
print("1. Distance is the biggest factor in fare (correlation about",
      round(df["Travel_Distance_km"].corr(df["Ticket_Fare_INR"]), 2), ")")
print("2. Smart Card users pay the least on average.")
print("3. Peak hour trips and Airport Express trips cost more.")
print("4. Each interchange adds to the fare.")

# ---------- 9. saving the results ----------
results_path = PROCESSED_DIR / "dmrc_fare_results.csv"
line_summary_path = REPORTS_DIR / "line_summary.csv"
df.to_csv(results_path, index=False)
line_summary.round(2).to_csv(line_summary_path)
print(f"\nSaved {results_path}")
print(f"Saved {line_summary_path}")
