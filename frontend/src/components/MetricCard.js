import React from "react";

function MetricCard({ title, value, icon, status }) {
  return (
    <div className="metric-card">

      <div className="metric-header">
        <span>{icon}</span>
        <h3>{title}</h3>
      </div>

      <h1>{value}</h1>

      <p>{status}</p>

    </div>
  );
}

export default MetricCard;