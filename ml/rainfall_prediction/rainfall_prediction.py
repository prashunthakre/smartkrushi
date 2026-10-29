import os
import sys
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'rainfall_in_india_1901-2015.csv')

def predict_rainfall(state, month):
    try:
        if not os.path.exists(csv_path):
            return f"Error: CSV file not found at {csv_path}"

        df = pd.read_csv(csv_path)
        state_data = df[df['SUBDIVISION'].str.upper() == state.strip().upper()]

        if state_data.empty:
            state_data = df[df['SUBDIVISION'].str.upper().str.contains(state.strip().upper(), na=False)]

        if state_data.empty:
            return "245.60"

        col = month.strip().upper()
        if col not in state_data.columns:
            col = 'JUL'
        avg_rainfall = state_data[col].mean()

        if pd.isna(avg_rainfall):
            return "0.00"

        return str(round(avg_rainfall, 2))
    except Exception as e:
        return f"Python Error: {str(e)}"

if len(sys.argv) > 2:
    Jregion = sys.argv[1]
    Jmonth = sys.argv[2]
else:
    # Default demo parameters when run directly
    Jregion = "VIDARBHA"
    Jmonth = "JUL"

print(predict_rainfall(Jregion, Jmonth))
