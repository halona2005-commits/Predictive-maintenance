import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function FaultPrediction() {

  const [prediction, setPrediction] = useState(null);
  const [status, setStatus] = useState(null);

  const loadData = async () => {
    try {

      const [p, s] = await Promise.all([
        fetch(`${API}/predict`).then(r => r.json()),
        fetch(`${API}/status`).then(r => r.json())
      ]);

      setPrediction(p);
      setStatus(s);

    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {

    loadData();

    const timer = setInterval(loadData, 5000);

    return () => clearInterval(timer);

  }, []);

  if (!prediction || !status)
    return <h2>Loading...</h2>;

  const risk = prediction.risk_score * 100;

  let failureWindow = "7+ Days";

  if (risk >= 80)
    failureWindow = "Within 24 Hours";
  else if (risk >= 60)
    failureWindow = "1–3 Days";
  else if (risk >= 40)
    failureWindow = "3–7 Days";

  let cause = "System operating normally.";

  switch (status.fault_type) {

    case "CPU":
      cause = "High CPU utilization and abnormal processing load.";
      break;

    case "MEMORY":
      cause = "Memory pressure and reduced available RAM.";
      break;

    case "DISK":
      cause = "High disk activity and write throughput.";
      break;

    default:
      cause = "No significant anomaly detected.";

  }

  let recommendation = "Continue monitoring.";

  if (risk >= 80)
    recommendation =
      "Immediate maintenance recommended. Investigate system before failure.";

  else if (risk >= 60)
    recommendation =
      "Schedule maintenance as soon as possible.";

  else if (risk >= 40)
    recommendation =
      "Increase monitoring frequency.";

  return (

    <div>

      <h2 style={{ marginBottom: 20 }}>
        Fault Prediction
      </h2>

      {risk >= 60 && (

        <div
          className="card"
          style={{
            background: "#5b1111",
            marginBottom: 20,
            border: "1px solid red"
          }}
        >
          ⚠ Warning: High Risk Condition Detected
        </div>

      )}

      <div
        className="card"
        style={{
          marginBottom: 20
        }}
      >

        <h3>Predicted Fault</h3>

        <h1
          style={{
            marginTop: 15,
            color: "#60a5fa"
          }}
        >
          {status.fault_type}
        </h1>

      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2,1fr)",
          gap: 20
        }}
      >

        <div className="card">

          <h3>Severity</h3>

          <div
            style={{
              marginTop: 15,
              fontSize: 22,
              color: "#f87171",
              fontWeight: "bold"
            }}
          >
            {status.severity_level}
          </div>

        </div>

        <div className="card">

          <h3>Probability</h3>

          <div
            style={{
              marginTop: 15,
              fontSize: 22,
              color: "#4ade80",
              fontWeight: "bold"
            }}
          >
            {risk.toFixed(1)}%
          </div>

        </div>

        <div className="card">

          <h3>Estimated Failure Window</h3>

          <p
            style={{
              marginTop: 15,
              fontSize: 18
            }}
          >
            {failureWindow}
          </p>

        </div>

        <div className="card">

          <h3>Likely Cause</h3>

          <p
            style={{
              marginTop: 15
            }}
          >
            {cause}
          </p>

        </div>

      </div>

      <div
        className="card"
        style={{
          marginTop: 20
        }}
      >

        <h3>Recommendation</h3>

        <p
          style={{
            marginTop: 15,
            lineHeight: 1.7
          }}
        >
          {recommendation}
        </p>

      </div>

    </div>

  );

}