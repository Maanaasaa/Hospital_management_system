from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import joblib
import os

app = Flask(__name__)

# 🔹 Dataset Directory
DATA_DIR = r"E:\project\data"

# 🔹 Load Model & Scaler
rf_model = joblib.load(r"E:\project\random_forest_model.pkl")
scaler = joblib.load(r"E:\project\random_scaler.pkl")

# 🔹 Load Datasets
description_df = pd.read_csv(os.path.join(DATA_DIR, "description.csv"))[["Disease", "Description"]]
precautions_df = pd.read_csv(os.path.join(DATA_DIR, "precautions_df.csv"))[["Disease", "Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]]
medications_df = pd.read_csv(os.path.join(DATA_DIR, "medications.csv"))[["Disease", "Medication"]]
diets_df = pd.read_csv(os.path.join(DATA_DIR, "diets.csv"))[["Disease", "Diet"]]
workouts_df = pd.read_csv(os.path.join(DATA_DIR, "workout_df.csv"))[["disease", "workout"]]

# 🔹 Load Symptoms Dataset
training_data = pd.read_csv(os.path.join(DATA_DIR, "Training.csv"))
all_symptoms = training_data.columns[:-1]

# 🔹 Predict Disease
def predict_disease(symptoms):
    input_data = np.zeros(len(all_symptoms))
    for symptom in symptoms:
        if symptom in all_symptoms:
            input_data[list(all_symptoms).index(symptom)] = 1
    input_data = scaler.transform([input_data])
    return rf_model.predict(input_data)[0]

# 🔹 Get Disease Information
def get_disease_info(disease):
    description = description_df.loc[description_df['Disease'] == disease, 'Description'].values
    precautions = precautions_df.loc[precautions_df['Disease'] == disease, ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']].values
    medications = medications_df.loc[medications_df['Disease'] == disease, 'Medication'].values
    diet = diets_df.loc[diets_df['Disease'] == disease, 'Diet'].values
    workout = workouts_df.loc[workouts_df['disease'] == disease, 'workout'].values

    return {
        "disease": disease,
        "description": description[0] if len(description) > 0 else "No description available",
        "precautions": precautions[0].tolist() if len(precautions) > 0 else ["No precautions available"],
        "medications": medications.tolist() if len(medications) > 0 else ["No medications available"],
        "diet": diet[0] if len(diet) > 0 else "No diet available",
        "workout": workout[0] if len(workout) > 0 else "No workout available",
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    symptoms = request.json.get("symptoms", "").split(",")
    symptoms = [s.strip() for s in symptoms]
    predicted_disease = predict_disease(symptoms)
    return jsonify(get_disease_info(predicted_disease))

if __name__ == "__main__":
    app.run(debug=True)
