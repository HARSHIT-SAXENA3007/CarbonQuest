import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = (process.env.REACT_APP_API_URL || "").replace(/\/+$/, "");

function buildApiUrl(path) {
  if (!API_BASE_URL) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

function App() {
  const [form, setForm] = useState({
    km: "",
    kwh: "",
    meat_meals: "",
    inr: ""
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      setError("");
      const res = await axios.post(buildApiUrl("/api/calculate"), {
        km: parseFloat(form.km),
        kwh: parseFloat(form.kwh),
        meat_meals: parseInt(form.meat_meals, 10),
        inr: parseFloat(form.inr)
      });
      setResult(res.data);
    } catch (err) {
      setResult(null);
      setError(err.response?.data?.error || "Could not connect to the backend.");
    }
  };

  return (
    <div className="App">
      <h1 className="main-heading">CarbonQuest</h1>
      <div className="form">
        <input name="km" placeholder="Km traveled" value={form.km} onChange={handleChange} />
        <input name="kwh" placeholder="Electricity used (kWh)" value={form.kwh} onChange={handleChange} />
        <input name="meat_meals" placeholder="Meat meals/week" value={form.meat_meals} onChange={handleChange} />
        <input name="inr" placeholder="Amount spent on shopping" value={form.inr} onChange={handleChange} />
        <button onClick={handleSubmit}>Calculate</button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result">
          <h2>Emissions Breakdown</h2>
          <ul>
            <li>Transport: {result.emissions.Transport.toFixed(2)} kg CO2</li>
            <li>Electricity: {result.emissions.Electricity.toFixed(2)} kg CO2</li>
            <li>Food: {result.emissions.Food.toFixed(2)} kg CO2</li>
            <li>Shopping: {result.emissions.Shopping.toFixed(2)} kg CO2</li>
            <li>Total: {result.emissions.Total.toFixed(2)} kg CO2</li>
          </ul>
          <h3>Highest Impact: {result.highest_contributor}</h3>
          <p>Suggestion:</p>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: "1rem" }}>{result.suggested_action}</pre>
          <h3>Emission Cluster Summary</h3>
          <p style={{ whiteSpace: "pre-wrap", fontSize: "1rem", marginBottom: "20px" }}>
            {result.cluster_summary}
          </p>
          <a
            href={buildApiUrl(result.plot_url || "/api/cluster-plot")}
            download="cluster_plot.png"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-block",
              padding: "10px 20px",
              backgroundColor: "#4CAF50",
              color: "white",
              textDecoration: "none",
              borderRadius: "8px",
              fontWeight: "bold",
              marginTop: "10px"
            }}
          >
            Download Cluster Plot
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
