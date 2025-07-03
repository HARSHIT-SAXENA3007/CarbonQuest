import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    km: "",
    kwh: "",
    meat_meals: "",
    inr: ""
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/calculate", {
        km: parseFloat(form.km),
        kwh: parseFloat(form.kwh),
        meat_meals: parseInt(form.meat_meals),
        inr: parseFloat(form.inr)
      });
      setResult(res.data);
    } catch (err) {
      alert("⚠ Error connecting to Flask backend");
    }
  };

  return (
    <div className="App">
      <h1 className="main-heading">🌍 CarbonQuest</h1>
      <div className="form">
        <input name="km" placeholder="Km traveled" value={form.km} onChange={handleChange} />
        <input name="kwh" placeholder="Electricity used (kWh)" value={form.kwh} onChange={handleChange} />
        <input name="meat_meals" placeholder="Meat meals/week" value={form.meat_meals} onChange={handleChange} />
        <input name="inr" placeholder="₹ spent on shopping" value={form.inr} onChange={handleChange} />
        <button onClick={handleSubmit}>Calculate</button>
      </div>

      {result && (
        <div className="result">
          <h2>📊 Emissions Breakdown:</h2>
          <ul>
            <li>🚗 Transport: {result.emissions.Transport.toFixed(2)} kg CO₂</li>
            <li>⚡ Electricity: {result.emissions.Electricity.toFixed(2)} kg CO₂</li>
            <li>🍗 Food: {result.emissions.Food.toFixed(2)} kg CO₂</li>
            <li>🛍️ Shopping: {result.emissions.Shopping.toFixed(2)} kg CO₂</li>
            <li>🧮 Total: {result.emissions.Total.toFixed(2)} kg CO₂</li>
          </ul>
          <h3>📌 Highest Impact: {result.highest_contributor}</h3>
          <p>
          💡 Suggestion:
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '1rem' }}>{result.suggested_action}</pre>
          </p>
          <h3>🧠 Emission Cluster Summary</h3>
          <p 
           style={{ whiteSpace: 'pre-wrap', fontSize: '1rem', marginBottom: '20px' }}>
           {result.cluster_summary}
          </p>
          <a
           href={`http://127.0.0.1:5000/cluster-plot`}
           download="cluster_plot.png"
           target="_blank"
           rel="noopener noreferrer"
           style={{
           display: 'inline-block',
           padding: '10px 20px',
           backgroundColor: '#4CAF50',
           color: 'white',
           textDecoration: 'none',
           borderRadius: '8px',
           fontWeight: 'bold',
           marginTop: '10px'
          }}
          >
         📥 Download Cluster Plot
        </a>

        </div>
      )}
    </div>
  );
}

export default App;