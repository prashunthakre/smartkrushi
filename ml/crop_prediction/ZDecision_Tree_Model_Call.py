import pandas as pd
import numpy as np
import joblib
import sys
import os

# 1. Define the Classes required to load the model
# (These must match the training script EXACTLY for pickle to work)

header = ['State_Name', 'District_Name', 'Season', 'Crop']

class Question:
    def __init__(self, column, value):
        self.column = column
        self.value = value
    def match(self, example):
        val = example[self.column]
        return val == self.value
    def match2(self, example):
        if example == 'True' or example == 'true' or example == '1':
            return True
        else:
            return False
    def __repr__(self):
        return "Is %s %s %s?" % (header[self.column], "==", str(self.value))

def class_counts(Data):
    counts = {}
    for row in Data:
        label = row[-1]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

class Leaf:
    def __init__(self, Data):
        self.predictions = class_counts(Data)

class Decision_Node:
    def __init__(self, question, true_branch, false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch

def print_leaf(counts):
    total = sum(counts.values()) * 1.0
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs

def classify(row, node):
    if isinstance(node, Leaf):
        return node.predictions
    if node.question.match(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)

# 2. Main Execution Logic

try:
    # Get the directory where THIS python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the absolute path to the .pkl file
    model_path = os.path.join(script_dir, 'filetest2.pkl')

    # Load the model
    dt_model_final = joblib.load(model_path)

    # 3. Get Arguments from PHP and Format them
    # We use .title() because CSVs usually have "Shimla", but Input might be "SHIMLA"
    # We use .strip() to remove accidental spaces
    if len(sys.argv) > 3:
        state = sys.argv[1].strip().title()
        district = sys.argv[2].strip().title()
        season = sys.argv[3].strip().title()
    else:
        # Default/Fallback for testing if no args provided
        state = "Maharashtra" 
        district = "Pune"
        season = "Kharif"

    testing_data = [[state, district, season]]

    # 4. Predict
    Predict_dict = {}
    for row in testing_data:
        # Get the prediction
        Predict_dict = print_leaf(classify(row, dt_model_final))

    # 5. Print Result for PHP to catch
    if not Predict_dict:
        print("No suitable crop found for this data.")
    else:
        # Print only the keys (Crop names) separated by comma
        crops = list(Predict_dict.keys())
        print(", ".join(crops))

except Exception as e:
    # This prints errors to the PHP screen so you know what went wrong
    print(f"Error in Python: {str(e)}")