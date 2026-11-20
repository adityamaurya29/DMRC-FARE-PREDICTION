import numpy as np
import pandas as pd

df = pd.read_csv('dmrc_fare_prediction.csv')

for col in df.columns:
  df[col] = df[col].astype(str).str.strip()

dirty_nulls = ['nan', 'None', 'unknown', 'not available', '??', '']
df.replace(dirty_nulls, np.nan, inplace=True)

station_overrides = {
    'ina': 'INA',
    'igi airport (t3)': 'IGI Airport (T3)',
    'terminal 1-igi airport': 'Terminal 1-IGI Airport',
    'mayur vihar-i': 'Mayur Vihar-I',
    'shaheed sthal (new bus adda)': 'Shaheed Sthal (New Bus Adda)',
}


def clean_station(val):
  if pd.isna(val):
    return val
  return station_overrides.get(val.lower(), val.title())


for col in ['Origin_Station', 'Destination_Station']:
  df[col] = df[col].apply(clean_station)

df['Corridor_Line'] = df['Corridor_Line'].apply(
    lambda x: (
        'Orange/Airport Express'
        if pd.notna(x) and x.lower() == 'orange/airport express'
        else (x.title() if pd.notna(x) else x)
    )
)

ticket_map = {
    'qr mobile ticket': 'QR Mobile Ticket',
    'smart card': 'Smart Card',
    'token': 'Token',
}
df['Ticket_Type'] = df['Ticket_Type'].str.lower().map(ticket_map)

numeric_cols = [
    'Travel_Distance_km',
    'Interchange_Count',
    'Is_Airport_Express',
    'Is_Peak_Hour',
    'Ticket_Fare_INR',
]
for col in numeric_cols:
  df[col] = pd.to_numeric(df[col], errors='coerce')

df_clean = df.groupby('Trip_ID', as_index=False).first()

int_cols = ['Interchange_Count', 'Is_Airport_Express', 'Is_Peak_Hour']
df_clean[int_cols] = df_clean[int_cols].astype(int)

df_clean.to_csv('dmrc_fare_cleaned.csv', index=False)