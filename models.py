from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

# User Model (For Admin, Doctor, and Patient)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "admin", "doctor", "patient"

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


# Doctors Table
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)


# Patients Table
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)


class ConsultationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=True)
    status = db.Column(db.String(20), default="Pending")  # Pending, Assigned, Completed
    patient = db.relationship("Patient", backref="consultations")
    doctor = db.relationship("Doctor", backref="assigned_patients")
from sqlalchemy.sql import func  # Import SQLAlchemy's function for timestamps


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultation_request.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    consultation = db.relationship("ConsultationRequest", backref="comments")
    doctor = db.relationship("Doctor", backref="comments")


