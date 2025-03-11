function predictDisease() {
    let symptoms = document.getElementById("symptoms").value.trim();
    let predictBtn = document.getElementById("predict-btn");
    let loading = document.getElementById("loading");
    let resultDiv = document.getElementById("result");

    if (!symptoms) {
        alert("Please enter symptoms!");
        return;
    }

    // Show loading animation and disable button
    loading.classList.remove("hidden");
    resultDiv.classList.add("hidden");
    resultDiv.classList.remove("show-result");
    predictBtn.disabled = true;
    predictBtn.innerText = "Predicting...";

    setTimeout(() => {
        fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symptoms: symptoms })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Hide loading and show results with animation
            loading.classList.add("hidden");
            resultDiv.classList.remove("hidden");
            setTimeout(() => {
                resultDiv.classList.add("show-result");
            }, 100);

            // Display result values
            document.getElementById("disease").innerText = data.disease;
            document.getElementById("description").innerText = data.description;
            document.getElementById("medications").innerText = data.medications.join(", ");
            document.getElementById("precautions").innerText = data.precautions.join(", ");
            document.getElementById("diet").innerText = data.diet;
            document.getElementById("workout").innerText = data.workout;

            // Reset button
            predictBtn.disabled = false;
            predictBtn.innerText = "🔍 Predict";
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Something went wrong. Please try again.");
        });
    }, 3000);  // Simulated delay for animation
}
