import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function Alerts() {

  const [alerts, setAlerts] = useState([]);

  async function loadAlerts() {
    try {
      const res = await fetch(`${API}/alerts`);
      const data = await res.json();
      setAlerts(data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadAlerts();

    const timer = setInterval(loadAlerts, 10000);

    return () => clearInterval(timer);
  }, []);

  const clearResolved = () => {
    setAlerts(alerts.filter(a => !a.resolved_at));
  };

  const rowColor = (severity) => {

    switch ((severity || "").toUpperCase()) {

      case "CRITICAL":
        return "#5b1111";

      case "HIGH":
        return "#4d2508";

      case "MEDIUM":
        return "#554400";

      case "LOW":
        return "#0d2a55";

      default:
        return "#131720";

    }
  };

  return (

    <div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 20
        }}
      >

        <h2>System Alerts</h2>

        <button
          onClick={clearResolved}
          style={{
            background: "#2563eb",
            color: "white",
            border: "none",
            padding: "10px 18px",
            borderRadius: 8
          }}
        >
          Clear Resolved Alerts
        </button>

      </div>

      <div className="card">

        <table>

          <thead>

            <tr>
              <th>Time</th>
              <th>Alert</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Action</th>
            </tr>

          </thead>

          <tbody>

            {alerts.length === 0 && (

              <tr>
                <td colSpan="5">
                  No Alerts
                </td>
              </tr>

            )}

            {alerts.map(alert => (

              <tr
                key={alert.id}
                style={{
                  background: rowColor(alert.severity)
                }}
              >

                <td>
                  {new Date(alert.timestamp)
                    .toLocaleString()}
                </td>

                <td>
                  {alert.alert_type}
                </td>

                <td>

                  <strong>
                    {alert.severity}
                  </strong>

                </td>

                <td>

                  {alert.resolved_at
                    ? "Resolved"
                    : "Active"}

                </td>

                <td
                  style={{
                    fontSize: 20
                  }}
                >
                  🔔
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );

}