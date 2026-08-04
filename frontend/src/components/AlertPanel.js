import React from "react";

export default function AlertPanel({ alerts = [] }) {
  return (
    <div className="component-card">
      <h3>🚨 Recent Alerts</h3>

      {alerts.length === 0 ? (
        <p className="no-alerts">No Active Alerts</p>
      ) : (
        alerts.map((alert) => (
          <div
            key={alert.id}
            className={`alert-card ${alert.severity?.toLowerCase()}`}
          >
            <div className="alert-title">
              {alert.alert_type}
            </div>

            <div className="alert-sub">
              {alert.fault_type}
            </div>

            <div className="alert-time">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}