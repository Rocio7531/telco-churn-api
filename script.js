const API_URL = "https://telco-churn-api-cj8e.onrender.com/predict";

document.getElementById("clear-btn").addEventListener("click", function () {
    document.getElementById("churn-form").reset();
    document.getElementById("result").innerHTML = "";
});
//Form Submit
document.getElementById("churn-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const payload = {
        gender: document.getElementById("gender").value,
        Partner: document.getElementById("Partner").value,
        Dependents: document.getElementById("Dependents").value,
        PhoneService: document.getElementById("PhoneService").value,
        MultipleLines: document.getElementById("MultipleLines").value,
        InternetService: document.getElementById("InternetService").value,
        OnlineSecurity: document.getElementById("OnlineSecurity").value,
        OnlineBackup: document.getElementById("OnlineBackup").value,
        DeviceProtection: document.getElementById("DeviceProtection").value,
        TechSupport: document.getElementById("TechSupport").value,
        StreamingTV: document.getElementById("StreamingTV").value,
        StreamingMovies: document.getElementById("StreamingMovies").value,
        Contract: document.getElementById("Contract").value,
        PaymentMethod: document.getElementById("PaymentMethod").value,
        tenure: Number(document.getElementById("tenure").value),
        MonthlyCharges: Number(document.getElementById("MonthlyCharges").value),
        TotalCharges: Number(document.getElementById("TotalCharges").value)
    };

    const resultBox = document.getElementById("result");
    resultBox.innerHTML = "Calculating prediction...";

    try {
        const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json", //This tells the API that the request body is in JSON format
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        resultBox.innerHTML = "Error: " + JSON.stringify(data);
        return;
    }

    const probability = (data.churn_probability * 100).toFixed(2);

    if (data.prediction === 1) {
        resultBox.innerHTML = `⚠️ Customer at risk of churn. Probability: ${probability}%`;
        resultBox.style.background = "#ffe0e0";
    } else {
        resultBox.innerHTML = `✅ Customer likely to be retained. Churn probability: ${probability}%`;
        resultBox.style.background = "#e0ffe8";
    }
    } catch (error) {
        resultBox.innerHTML = "Unable to connect to the API";
    }
});