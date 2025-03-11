async function fetchDoctors() {
    try {
        let response = await fetch('/api/doctors');
        let data = await response.json();
        let doctorList = document.getElementById("doctor-list");
        doctorList.innerHTML = "";

        if (data.length === 0) {
            doctorList.innerHTML = "<li>No doctors available.</li>";
            return;
        }

        data.forEach(doctor => {
            let listItem = document.createElement("li");
            listItem.innerHTML = `
                ${doctor.name} (${doctor.specialization})
                <button onclick="removeDoctor(${doctor.id})">❌ Remove</button>
            `;
            doctorList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error fetching doctors:", error);
    }
}

async function fetchPatients() {
    try {
        let response = await fetch('/api/patients');
        let data = await response.json();
        let patientList = document.getElementById("patient-list");
        patientList.innerHTML = "";

        if (data.length === 0) {
            patientList.innerHTML = "<li>No patients available.</li>";
            return;
        }

        data.forEach(patient => {
            let listItem = document.createElement("li");
            listItem.innerHTML = `
                ${patient.name} (${patient.blood_group}) - Assigned Doctor: 
                ${patient.assigned_doctor || "Not Assigned"}
                <button onclick="removePatient(${patient.id})">❌ Remove</button>
            `;
            patientList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error fetching patients:", error);
    }
}

async function doctorsList() {
    let doctorOptions = "";
    try {
        let response = await fetch('/api/doctors');
        let doctors = await response.json();
        doctors.forEach(doctor => {
            doctorOptions += `<option value="${doctor.id}">${doctor.name}</option>`;
        });
    } catch (error) {
        console.error("Error fetching doctors:", error);
    }
    return doctorOptions;
}

async function fetchConsultations() {
    try {
        let response = await fetch('/api/consultations');
        let data = await response.json();
        let consultationList = document.getElementById("consultation-list");
        consultationList.innerHTML = "";

        let doctorOptions = await doctorsList();

        data.forEach(request => {
            let listItem = document.createElement("li");
            listItem.innerHTML = `
                ${request.patient_name} - Status: ${request.status}
                <form method="POST" class="assign-form">
                    <input type="hidden" name="patient_id" value="${request.patient_id}">
                    <select name="doctor_id">${doctorOptions}</select>
                    <button type="submit">Assign Doctor</button>
                </form>
            `;
            consultationList.appendChild(listItem);
        });

        document.querySelectorAll(".assign-form").forEach(form => {
            form.addEventListener("submit", assignDoctor);
        });

    } catch (error) {
        console.error("Error fetching consultations:", error);
    }
}

async function assignDoctor(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let patient_id = formData.get("patient_id");
    let doctor_id = formData.get("doctor_id");

    try {
        let response = await fetch("/assign_doctor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ patient_id, doctor_id })
        });

        let data = await response.json();
        alert(data.message);
        fetchPatients();
        fetchConsultations();
    } catch (error) {
        console.error("Error:", error);
    }
}

setInterval(fetchConsultations, 5000);
fetchDoctors();
fetchPatients();
fetchConsultations();
