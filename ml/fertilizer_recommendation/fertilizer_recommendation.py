import os
import sys
import json
import warnings
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

def clean_val(val, is_num=True):
    try:
        v = json.loads(val)
    except Exception:
        v = val
    if is_num:
        try:
            return float(v)
        except Exception:
            return 25.0
    return str(v).strip()

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "fertilizer_recommendation.csv")
data = pd.read_csv(csv_path)

le_soil = LabelEncoder()
data['Soil Type'] = le_soil.fit_transform(data['Soil Type'].astype(str).str.strip())
le_crop = LabelEncoder()
data['Crop Type'] = le_crop.fit_transform(data['Crop Type'].astype(str).str.strip())

X = data.iloc[:, :8]
y = data.iloc[:, -1]

dtc = DecisionTreeClassifier(random_state=0)
dtc.fit(X, y)

if len(sys.argv) > 8:
    jsonn = clean_val(sys.argv[1], True)
    jsonp = clean_val(sys.argv[2], True)
    jsonk = clean_val(sys.argv[3], True)
    jsont = clean_val(sys.argv[4], True)
    jsonh = clean_val(sys.argv[5], True)
    jsonsm = clean_val(sys.argv[6], True)
    jsonsoil = clean_val(sys.argv[7], False)
    jsoncrop = clean_val(sys.argv[8], False)
else:
    # Default demo inputs when run directly in VS Code / Terminal
    jsonn, jsonp, jsonk = 37.0, 0.0, 0.0
    jsont, jsonh, jsonsm = 26.0, 52.0, 38.0
    jsonsoil, jsoncrop = "Sandy", "Maize"

soil_classes = list(le_soil.classes_)
crop_classes = list(le_crop.classes_)
soil_match = next((s for s in soil_classes if s.lower() == jsonsoil.lower()), soil_classes[0])
crop_match = next((c for c in crop_classes if c.lower() == jsoncrop.lower()), crop_classes[0])

soil_enc = le_soil.transform([soil_match])[0]
crop_enc = le_crop.transform([crop_match])[0]

user_input = [[jsont, jsonh, jsonsm, soil_enc, crop_enc, jsonn, jsonk, jsonp]]
fertilizer_name = dtc.predict(user_input)

print(str(fertilizer_name[0]))
