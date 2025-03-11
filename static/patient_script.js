document.getElementById("consultation-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Stop normal form submission

    fetch("/request_consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})  // Empty body as we don't need extra data
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("response-message").innerText = data.message;
    })
    .catch(error => console.error("Error:", error));
});
