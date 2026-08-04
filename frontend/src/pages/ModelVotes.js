import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

const MODEL_F1 = {
  "Random Forest": 98.62,
  "XGBoost": 98.81,
  "Isolation Forest": 87.61,
  "One-Class SVM": 87.12,
  "Compressed IF": 89.02,
  "LSTM ": 46.53
};

export default function ModelVotes() {

  const [prediction, setPrediction] = useState(null);

  const fetchPrediction = async () => {
    try {
      const res = await fetch(`${API}/predict`);
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPrediction();
    const timer = setInterval(fetchPrediction, 5000);
    return () => clearInterval(timer);
  }, []);

  if (!prediction) {
    return <h2>Loading...</h2>;
  }

  const models = prediction.models || {};
  const probabilities = prediction.probabilities || {};

  const anomalyCount = Object.values(models).filter(v => v === 1).length;

  return (
    <div>

      <h2 style={{ marginBottom: 20 }}>
        AI Model Voting System
      </h2>

      <div className="card">

        <table>

          <thead>

            <tr>
              <th>Model</th>
              <th>Vote</th>
              <th>Score</th>
              <th>Reason</th>
            </tr>

          </thead>

          <tbody>

            {Object.entries(models).map(([name, vote]) => {

              const confidence = (() => {
                 if (probabilities[name] !== undefined) {
                    return (probabilities[name] * 100).toFixed(2) + "%";
                }
                if (MODEL_F1[name] !== undefined) {
                    return MODEL_F1[name].toFixed(2) + "%";
                }
                return "N/A";
            })();

              const reason =
                vote === 1
                  ? `High ${prediction.fault_type} anomaly detected`
                  : "Normal operating pattern";
                  
                return (

                <tr key={name}>

                  <td>{name}</td>

                  <td>

                    <span
                      style={{
                        color: vote ? "#ef4444" : "#22c55e",
                        fontWeight: "bold"
                      }}
                    >
                      {vote ? "Anomaly" : "Normal"}
                    </span>

                  </td>

                  <td>{confidence}</td>

                  <td>{reason}</td>

                </tr>

              );

            })}

          </tbody>

        </table>

      </div>

      <div
        className="card"
        style={{
          marginTop: 20
        }}
      >

        <h3>Summary</h3>

        <p style={{ marginTop: 12 }}>

          <strong>
            {anomalyCount}/6
          </strong>{" "}
          models detected anomaly.

        </p>

        <div
          style={{
            marginTop: 20,
            display: "inline-block",
            padding: "10px 20px",
            borderRadius: 8,
            background:
              anomalyCount >= 3
                ? "#7f1d1d"
                : "#14532d",
            color: "white",
            fontWeight: "bold"
          }}
        >
          {anomalyCount >= 3
            ? "HIGH RISK"
            : "NORMAL"}
        </div>

      </div>

    </div>
  );
}