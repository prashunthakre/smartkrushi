import os
import sys
import json
import warnings
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

warnings.filterwarnings("ignore")

def parse_arg(val, default):
    try:
        return float(json.loads(val))
    except Exception:
        try:
            return float(val)
        except Exception:
            return default

if len(sys.argv) > 7:
    n_params = parse_arg(sys.argv[1], 90)
    p_params = parse_arg(sys.argv[2], 42)
    k_params = parse_arg(sys.argv[3], 43)
    t_params = parse_arg(sys.argv[4], 21)
    h_params = parse_arg(sys.argv[5], 82)
    ph_params = parse_arg(sys.argv[6], 6.5)
    r_params = parse_arg(sys.argv[7], 203)
else:
    # Default demo parameters when run directly in VS Code / Terminal
    n_params, p_params, k_params, t_params, h_params, ph_params, r_params = 90, 42, 43, 21, 82, 6.5, 203

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'Crop_recommendation.csv')
dataset = pd.read_csv(csv_path)

X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

classifier = RandomForestClassifier(n_estimators=10, criterion='entropy', random_state=0)
classifier.fit(X_train, y_train)

user_input = np.array([[n_params, p_params, k_params, t_params, h_params, ph_params, r_params]])
predictions = classifier.predict(user_input)

print(str(predictions[0]))
