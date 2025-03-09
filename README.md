

# **AI-Powered Disease Prediction and Patient Management System**  

## **Overview**  
This project is an AI-driven **disease prediction and patient management system** that allows users to input symptoms and receive **real-time disease predictions** using a **Random Forest Machine Learning model**. The system also includes a **patient-doctor consultation feature**, enabling doctors to provide advice and manage patient medical records.  

Built with a **Flask-based backend** and a **React.js (or similar) frontend**, the project integrates **MySQL for database management** and provides an interactive user experience.  

## **Features**  

### 🏥 **User Roles**  
1. **Patients:**  
   - Register and log in securely.  
   - Input symptoms and receive AI-based disease predictions.  
   - Request doctor consultations.  
   - View medical history and previous consultations.  
   - Log out securely.  

2. **Doctors:**  
   - View patient details and symptom history.  
   - Review AI-generated disease predictions.  
   - Provide medical advice via consultation records.  
   - Access patient medical history.  

3. **Admin:**  
   - Manage doctor and patient accounts.  
   - View and assign doctors to patient consultation requests.  

---

### 🤖 **AI-Based Disease Prediction**  
- Uses a **trained Random Forest Model** to predict diseases based on symptoms.  
- Preprocesses user input using a **scaler (random_scaler.pkl)** before feeding it into the model.  
- The dataset (`Training.csv`) contains symptoms and their corresponding diseases for accurate predictions.  

---

### 🔗 **Backend (Flask API & MySQL Database)**  
- The **Flask backend** provides RESTful API endpoints for:  
  - User authentication & session management.  
  - Storing and retrieving medical records.  
  - Processing and storing AI-based disease predictions.  
- **MySQL 8.0 Database** stores:  
  - Patient details & medical history.  
  - Doctor profiles & assigned consultations.  
  - Disease prediction results with timestamps.  

---

### 🎨 **Frontend (User Interface - React.js or Equivalent)**  
- User-friendly web interface for **symptom input, doctor consultations, and medical history tracking**.  
- Patients and doctors interact through **intuitive dashboards**.  
- Provides **real-time disease prediction results**.  

---

## **Tech Stack**  
| Component   | Technology Used  |
|-------------|-----------------|
| **Backend** | Flask (Python) |
| **Database** | MySQL 8.0 |
| **Machine Learning** | Random Forest, Scikit-learn |
| **Frontend** | React.js (or another JS framework) |
| **Deployment** | AWS / Heroku / DigitalOcean |

---

## **Installation & Setup**  


### **1. Backend Setup (Flask API)**  
#### **Install Dependencies**  
```bash
cd backend
pip install -r requirements.txt
```

#### **Run the Flask App**  
```bash
python app.py
```

### **2. Frontend Setup (React.js or other framework)**  
```bash
cd frontend
npm install
npm start
```

---

## **Future Enhancements**  
🚀 **Possible Improvements:**  
- Integrate **real-time chat** between doctors and patients.  
- Expand the AI model with **deep learning techniques** for better accuracy.  
- Add support for **mobile applications (Android/iOS)**.  

---
Key Components
Backend (Flask)

app.py: Main Flask application.

config.py: Configuration settings.

models.py: Defines database models.

model.ipynb: Jupyter Notebook, likely used for training/testing ML models.

random_forest_model.pkl: Trained Random Forest model for disease prediction.

random_scaler.pkl: Scaler for preprocessing input data.

Training.csv: Dataset used for training the model.

requirements.txt: List of dependencies.

Frontend (React or another framework)

Located in the medinsight-frontend directory.
Likely used for the user interface.

---

## **Contributing**  
Contributions are welcome! If you find bugs or want to enhance features, feel free to submit a pull request.  

---

