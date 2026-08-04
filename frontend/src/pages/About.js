import React from "react";

export default function About() {

  const technologies = [
    "Python",
    "FastAPI",
    "Machine Learning",
    "Scikit-learn",
    "TensorFlow",
    "SQLite",
    "React",
    "Chart.js",
    "JavaScript",
    "HTML5",
    "CSS3"
  ];

  return (

    <div>

      <h2 style={{ marginBottom: 20 }}>
        About
      </h2>

      <div className="card">

        <h1
          style={{
            color: "#4ade80",
            marginBottom: 8
          }}
        >
          Predictive Maintenance System
        </h1>

        <h3
          style={{
            color: "#94a3b8",
            marginBottom: 25
          }}
        >
          AI Powered Monitoring and Anomaly Detection
        </h3>

        <table>

          <tbody>

            <tr>
              <td><strong>Version</strong></td>
              <td>3.0.0</td>
            </tr>

            <tr>
              <td><strong>Developed By</strong></td>
              <td>
                Bondalakunta Yathiswar Reddy<br/>
                Halona Ann Siju<br/>
                Haripriya K P<br/>
                Hemanth Hitaishi S A
              </td>
            </tr>

            <tr>
              <td><strong>College</strong></td>
              <td>
                Sai Vidya Institute of Technology,
                Bengaluru
              </td>
            </tr>

            <tr>
              <td><strong>Project Guide</strong></td>
              <td>
                Poornima Gowda H S<br/>
                Dr. Vinod Desai
              </td>
            </tr>

          </tbody>

        </table>

      </div>

      <div
        className="card"
        style={{ marginTop: 20 }}
      >

        <h3>Technologies Used</h3>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            marginTop: 20
          }}
        >

          {technologies.map((tech) => (

            <div
              key={tech}
              style={{
                background: "#1e293b",
                padding: "10px 18px",
                borderRadius: 8,
                border: "1px solid #334155"
              }}
            >
              {tech}
            </div>

          ))}

        </div>

      </div>

      <div
        className="card"
        style={{ marginTop: 20 }}
      >

        <h3>Project Description</h3>

        <p
          style={{
            marginTop: 15,
            lineHeight: 1.8,
            color: "#cbd5e1"
          }}
        >
          This Predictive Maintenance System continuously monitors
          system health by collecting real-time performance metrics
          including CPU usage, memory utilization, disk activity,
          and process information.
        </p>

        <p
          style={{
            marginTop: 15,
            lineHeight: 1.8,
            color: "#cbd5e1"
          }}
        >
          Multiple AI models collaborate through an ensemble voting
          mechanism to detect anomalies, estimate system risk,
          identify likely fault types, and provide maintenance
          recommendations before failures occur.
        </p>

      </div>

    </div>

  );

}