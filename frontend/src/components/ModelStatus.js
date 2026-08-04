import React from "react";

export default function ModelStatus({ models = {}, modelF1 = {} }) {
  return (
    <div className="component-card">
      <h3>🤖 AI Model Status</h3>

      <table className="model-table">
        <thead>
          <tr>
            <th>Model</th>
            <th>F1</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {Object.entries(models).map(([name, vote]) => (
            <tr key={name}>
              <td>{name}</td>

              <td>{modelF1[name] || "--"}</td>

              <td>
                <span
                  className={
                    vote
                      ? "status-badge anomaly"
                      : "status-badge normal"
                  }
                >
                  {vote ? "ANOMALY" : "NORMAL"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}