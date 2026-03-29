import pandas as pd
import os

def calculate_risk():
    csv_path = os.path.join(os.path.dirname(__file__), "data.csv")
    df = pd.read_csv(csv_path)
    df['risk'] = df['Severity']
    return df[['Lat', 'Lng', 'risk']].to_dict(orient='records')
