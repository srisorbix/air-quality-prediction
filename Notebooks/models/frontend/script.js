const form = document.getElementById("predictionForm");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = {
        PT08_S1_CO: Number(document.getElementById("PT08_S1_CO").value),
        PT08_S3_NOx: Number(document.getElementById("PT08_S3_NOx").value),
        PT08_S4_NO2: Number(document.getElementById("PT08_S4_NO2").value),
        PT08_S5_O3: Number(document.getElementById("PT08_S5_O3").value),

        Temperature: Number(document.getElementById("Temperature").value),
        Relative_Humidity: Number(document.getElementById("Relative_Humidity").value),
        Absolute_Humidity: Number(document.getElementById("Absolute_Humidity").value),

        C6H6_lag1: Number(document.getElementById("C6H6_lag1").value),
        C6H6_lag2: Number(document.getElementById("C6H6_lag2").value),
        C6H6_lag3: Number(document.getElementById("C6H6_lag3").value),
        C6H6_lag24: Number(document.getElementById("C6H6_lag24").value),

        hour: Number(document.getElementById("hour").value)
    };

    const actual = document.getElementById("actual_benzene").value;

    if (actual !== "") {
        data.actual_benzene = Number(actual);
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error("Prediction failed. Check the backend.");
        }

        const result = await response.json();

        document.getElementById("results").hidden = false;

        document.getElementById("predicted").innerHTML =
            "Predicted Benzene: " + result.predicted_benzene;

        document.getElementById("pollution").innerHTML =
            "Pollution Status: " + result.pollution_status;

        document.getElementById("anomaly").innerHTML =
            "Anomaly Status: " + result.anomaly_status;

    } catch (error) {
        alert("Error connecting to backend. Make sure the FastAPI server is running.");
        console.error(error);
    }
});