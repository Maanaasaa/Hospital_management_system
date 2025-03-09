function predictDisease() {
    let symptoms = document.getElementById("symptoms").value.trim();
    let loading = document.getElementById("loading");
    let resultDiv = document.getElementById("result");

    if (!symptoms) {
        alert("Please enter symptoms!");
        return;
    }

    loading.classList.remove("hidden");
    resultDiv.classList.add("hidden");

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

            loading.classList.add("hidden");
            resultDiv.classList.remove("hidden");

            document.getElementById("disease").innerText = data.disease;
            document.getElementById("description").innerText = data.description;
            document.getElementById("medications").innerText = data.medications.join(", ");
            document.getElementById("precautions").innerText = data.precautions.join(", ");
            document.getElementById("diet").innerText = data.diet;
            document.getElementById("workout").innerText = data.workout;
        })
        .catch(error => alert("Something went wrong!"));
    }, 3000);
}
