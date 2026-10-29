import os
import sys
import json
import warnings
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore")

def clean_arg(val, default):
    try:
        return json.loads(val)
    except Exception:
        return val if val else default

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "crop_production_karnataka.csv")
df = pd.read_csv(csv_path)

df = df.drop(['Crop_Year'], axis=1)
df = df.dropna(subset=['Production', 'Area'])

X = df.drop(['Production'], axis=1)
y = df['Production']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

categorical_cols = ['State_Name', 'District_Name', 'Season', 'Crop']
ohe = OneHotEncoder(handle_unknown='ignore')
ohe.fit(X_train[categorical_cols])

X_train_categorical = ohe.transform(X_train[categorical_cols])
X_train_final = np.hstack((X_train_categorical.toarray(), X_train.drop(categorical_cols, axis=1).values))

model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
model.fit(X_train_final, y_train)

if len(sys.argv) > 5:
    Jstate = str(clean_arg(sys.argv[1], "Karnataka")).strip()
    Jdistrict = str(clean_arg(sys.argv[2], "BAGALKOT")).strip()
    Jseason = str(clean_arg(sys.argv[3], "Kharif")).strip()
    Jcrops = str(clean_arg(sys.argv[4], "Rice")).strip()
    try:
        Jarea = float(clean_arg(sys.argv[5], 100.0))
    except Exception:
        Jarea = 100.0
else:
    # Default demo parameters when run directly in VS Code / Terminal
    Jstate, Jdistrict, Jseason, Jcrops, Jarea = "Karnataka", "BAGALKOT", "Kharif", "Rice", 197.0

user_input = pd.DataFrame([[Jstate, Jdistrict, Jseason, Jcrops, Jarea]],
                          columns=['State_Name', 'District_Name', 'Season', 'Crop', 'Area'])
user_input_categorical = ohe.transform(user_input[categorical_cols])
user_input_final = np.hstack((user_input_categorical.toarray(), user_input[['Area']].values.astype(float)))

prediction = model.predict(user_input_final)
print(str(round(float(prediction[0]), 2)))
