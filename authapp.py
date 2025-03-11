from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import joblib
import pandas as pd
import numpy as np
from models import db, User  # Ensure models.py contains User model
from config import Config
from models import *  

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB & Migrations
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        role = request.form.get("role")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# 🔹 Load Trained Model & Scaler
rf_model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("random_scaler.pkl")

# 🔹 Load Datasets
description_df = pd.read_csv("description.csv")[['Disease', 'Description']]
precautions_df = pd.read_csv("precautions_df.csv")[['Disease', 'Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
medications_df = pd.read_csv("medications.csv")[['Disease', 'Medication']]
diets_df = pd.read_csv("diets.csv")[['Disease', 'Diet']]
workouts_df = pd.read_csv("workout_df.csv")[['disease', 'workout']]

# 🔹 Load Symptoms Dataset
training_data = pd.read_csv("Training.csv")
all_symptoms = training_data.columns[:-1]

# 🔹 Function to Predict Disease
def predict_disease(symptoms):
    input_data = np.zeros(len(all_symptoms))

    for symptom in symptoms:
        if symptom in all_symptoms:
            input_data[list(all_symptoms).index(symptom)] = 1

    input_data = np.array(input_data).reshape(1, -1)  # ✅ Ensure correct shape
    input_data = scaler.transform(input_data)  
    predicted_disease = rf_model.predict(input_data)[0]
    
    return predicted_disease

        
# 🔹 Function to Retrieve Disease Information
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

# 🔹 AI Disease Predictor UI
@app.route("/predict_page")
@login_required
def predict_page():
    return render_template("predict.html")  # Renders UI for symptom input

# 🔹 API Route for Disease Prediction
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    symptoms = request.json.get("symptoms", "").split(",")
    symptoms = [s.strip() for s in symptoms]

    predicted_disease = predict_disease(symptoms)
    disease_info = get_disease_info(predicted_disease)

    return jsonify(disease_info)

# ========================== ADMIN ROUTES ========================== #
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    doctors = Doctor.query.all()
    patients = Patient.query.all()
    consultations = ConsultationRequest.query.filter_by(status="Pending").all()

    return render_template(
        "admin_dashboard.html",
        doctors=doctors,
        patients=patients,
        consultations=consultations
    )
# Manage Doctors (Add, View, Remove)
@app.route("/manage_doctors", methods=["GET", "POST"])
@login_required
def manage_doctors():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        specialization = request.form.get("specialization")

        # Check if doctor with this email already exists
        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash("Doctor with this email already exists!", "danger")
            return redirect(url_for("manage_doctors"))

        new_doctor = Doctor(name=name, email=email, mobile=mobile, specialization=specialization)
        db.session.add(new_doctor)
        db.session.commit()
        flash("Doctor added successfully!", "success")

    doctors = Doctor.query.all()
    return render_template("manage_doctors.html", doctors=doctors)


# Manage Patients (Add, View, Remove)
@app.route("/manage_patients", methods=["GET", "POST"])
@login_required
def manage_patients():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        blood_group = request.form.get("blood_group")

        new_patient = Patient(name=name, email=email, mobile=mobile, blood_group=blood_group)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient added successfully!", "success")

    patients = Patient.query.all()
    return render_template("manage_patients.html", patients=patients)

@app.route("/admin/doctors/remove/<int:doctor_id>", methods=["DELETE"])
@login_required
def remove_doctor(doctor_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    doctor = Doctor.query.get(doctor_id)
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({"message": "Doctor removed successfully!"})

    return jsonify({"error": "Doctor not found"}), 404


@app.route("/admin/patients/remove/<int:patient_id>", methods=["DELETE"])
@login_required
def remove_patient(patient_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    patient = Patient.query.get(patient_id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({"message": "Patient removed successfully!"})

    return jsonify({"error": "Patient not found"}), 404


# Assign Doctor to Patient
@app.route("/assign_doctor", methods=["POST"])
@login_required
def assign_doctor():
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("dashboard"))

    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")

    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)

    if not patient or not doctor:
        flash("Invalid selection!", "danger")
        return redirect(url_for("admin_dashboard"))

    # Check if a consultation already exists
    consultation = ConsultationRequest.query.filter_by(patient_id=patient.id, status="Pending").first()

    if consultation:
        consultation.doctor_id = doctor.id
        consultation.status = "Assigned"
    else:
        new_consultation = ConsultationRequest(patient_id=patient.id, doctor_id=doctor.id, status="Assigned")
        db.session.add(new_consultation)

    db.session.commit()
    flash(f"Doctor {doctor.name} assigned to {patient.name}!", "success")
    return redirect(url_for("admin_dashboard"))




# ========================== DOCTOR ROUTES ========================== #

# Doctor Dashboard - View Assigned Patients
@app.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return redirect(url_for("dashboard"))

    doctor = Doctor.query.filter_by(email=current_user.email).first()
    if not doctor:
        flash("You are not registered as a doctor!", "danger")
        return redirect(url_for("dashboard"))

    assigned_patients = ConsultationRequest.query.filter_by(doctor_id=doctor.id, status="Assigned").all()
    return render_template("doctor_dashboard.html", patients=assigned_patients)

from datetime import datetime  # ✅ Fixes the datetime.utcnow() error

# Doctor - Add Comments (Medical History)
@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment():
    if current_user.role != "doctor":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("dashboard"))

    consultation_id = request.form.get("consultation_id")
    comment_text = request.form.get("comment")

    print(f"✅ DEBUG: Received consultation_id: {consultation_id}, Comment: {comment_text}")

    if not consultation_id or not comment_text:
        flash("Error: Consultation ID or comment is missing!", "danger")
        return redirect(url_for("doctor_dashboard"))

    doctor = db.session.get(Doctor, current_user.id)
    consultation = db.session.get(ConsultationRequest, consultation_id)

    if not doctor:
        flash("Error: Doctor not found!", "danger")
        return redirect(url_for("doctor_dashboard"))

    if not consultation:
        flash("Error: Consultation not found!", "danger")
        return redirect(url_for("doctor_dashboard"))

    # Insert comment into database
    new_comment = Comment(
        consultation_id=consultation.id,
        doctor_id=doctor.id,
        comment=comment_text.strip(),
        timestamp=datetime.utcnow()
    )

    db.session.add(new_comment)
    db.session.commit()
    print("✅ Comment successfully saved!")

    flash("Comment added successfully!", "success")
    return redirect(url_for("medical_history", patient_id=consultation.patient_id))

# ========================== VIEW PATIENT HISTORY ========================== #

@app.route("/patient/history/<int:patient_id>")
@login_required
def view_patient_history(patient_id):
    if current_user.role not in ["admin", "doctor"]:
        return redirect(url_for("dashboard"))

    patient = Patient.query.get(patient_id)
    consultations = ConsultationRequest.query.filter_by(patient_id=patient_id).all()
    comments = Comment.query.filter(Comment.consultation_id.in_([c.id for c in consultations])).all()

    return render_template("patient_history.html", patient=patient, consultations=consultations, comments=comments)

from models import db, Patient, ConsultationRequest

@app.route("/request_consultation", methods=["GET", "POST"])
@login_required
def request_consultation():
    if request.method == "GET":
        return render_template("request_consultation.html")  # Show form

    if current_user.role != "patient":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("dashboard"))

    # Get form data
    mobile = request.form.get("mobile")
    disease = request.form.get("disease")

    if not mobile or not disease:
        flash("All fields are required!", "danger")
        return redirect(url_for("request_consultation"))

    patient = Patient.query.filter_by(email=current_user.email).first()
    if not patient:
        flash("Patient record not found!", "danger")
        return redirect(url_for("dashboard"))

    # Check if there's already a pending request
    existing_request = ConsultationRequest.query.filter_by(patient_id=patient.id, status="Pending").first()
    if existing_request:
        flash("You already have a pending consultation request!", "warning")
        return redirect(url_for("dashboard"))

    # Create a new consultation request
    new_request = ConsultationRequest(patient_id=patient.id, status="Pending", disease_info=disease, mobile=mobile)
    db.session.add(new_request)
    db.session.commit()

    flash("Consultation request submitted successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/api/consultations")
@login_required
def get_consultations():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    consultations = ConsultationRequest.query.filter_by(status="Pending").all()
    consultations_data = [
        {
            "patient_name": consultation.patient.name,  # Fixed request.patient.name -> consultation.patient.name
            "status": consultation.status,
            "patient_id": consultation.patient.id
        }
        for consultation in consultations
    ]
    return jsonify(consultations_data)

@app.route("/api/doctors")
@login_required
def get_doctors():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    doctors = Doctor.query.all()
    doctors_data = [{"id": doctor.id, "name": doctor.name} for doctor in doctors]
    return jsonify(doctors_data)

@app.route("/add_consultation_note", methods=["POST"])
@login_required
def add_consultation_note():
    if current_user.role != "doctor":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("dashboard"))

    consultation_id = request.form.get("consultation_id")
    comment_text = request.form.get("comment")

    print(f"Received Data - Consultation ID: {consultation_id}, Comment: {comment_text}")  # Debugging

    if not consultation_id or not comment_text:
        flash("Consultation ID or Comment is missing!", "danger")
        return redirect(url_for("doctor_dashboard"))

    consultation = ConsultationRequest.query.get(consultation_id)
    if not consultation:
        flash("Consultation not found!", "danger")
        return redirect(url_for("doctor_dashboard"))

    if consultation.doctor_id != current_user.id:
        flash("You are not assigned to this patient!", "danger")
        return redirect(url_for("doctor_dashboard"))

    # Save the consultation note
    new_comment = Comment(
        consultation_id=consultation.id,
        doctor_id=current_user.id,
        comment=comment_text.strip()
    )
    db.session.add(new_comment)
    db.session.commit()

    print("Consultation note saved successfully!")  # Debugging
    flash("Consultation note saved successfully!", "success")
    return redirect(url_for("doctor_dashboard"))



from datetime import datetime  # ✅ Ensure correct datetime import
from sqlalchemy.orm import joinedload  # ✅ Ensure joinedload is imported

from sqlalchemy.orm import joinedload

@app.route("/medical_history/<int:patient_id>")
@login_required
def medical_history(patient_id):
    if current_user.role not in ["admin", "doctor"]:  # ✅ Allow both Admins & Doctors
        flash("Unauthorized access!", "danger")
        return redirect(url_for("dashboard"))

    patient = Patient.query.get_or_404(patient_id)

    # ✅ Ensure consultations load with comments and doctor details
    consultations = (
        ConsultationRequest.query
        .filter_by(patient_id=patient_id)
        .options(joinedload(ConsultationRequest.comments).joinedload(Comment.doctor))
        .all()
    )

    return render_template("medical_history.html", patient=patient, consultations=consultations)



if __name__ == "__main__":
    app.run(port=5001, debug=True)
