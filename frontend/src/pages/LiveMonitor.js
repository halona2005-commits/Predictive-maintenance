import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API = "http://127.0.0.1:8000";

export default function LiveMonitor() {
  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);

  const fetchData = async () => {
    try {
      const [h, p] = await Promise.all([
        fetch(`${API}/history`).then(r => r.json()),
        fetch(`${API}/predict`).then(r => r.json())
      ]);

      setHistory((h.metrics || []).slice(-30));
      setPrediction(p);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 5000);
    return () => clearInterval(timer);
  }, []);

  const labels = history.map((m) =>
    new Date(m.timestamp).toLocaleTimeString()
  );

  const cpu = history.map(m => m.cpu_percent);
  const memory = history.map(m => m.memory_percent);
  const disk = history.map(m => m.disk_write_mbps);

  const risk = history.map(() =>
    prediction ? prediction.risk_score * 100 : 0
  );

  const latest = history.length ? history[history.length - 1] : null;

  const makeChart = (label, color, data) => ({
    labels,
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: color,
        tension: 0.35
      }
    ]
  });

  const options = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: "#fff"
        }
      }
    },
    scales: {
      x: {
        ticks: { color: "#ccc" },
        grid: { color: "#222" }
      },
      y: {
        ticks: { color: "#ccc" },
        grid: { color: "#222" }
      }
    }
  };

  return (
    <div>

      <h2 style={{ marginBottom: 20 }}>Live System Monitor</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 20
        }}
      >

        <div className="card">
          <h3>CPU Usage %</h3>
          <Line
            data={makeChart("CPU", "#22c55e", cpu)}
            options={options}
          />
        </div>

        <div className="card">
          <h3>Memory Usage %</h3>
          <Line
            data={makeChart("Memory", "#3b82f6", memory)}
            options={options}
          />
        </div>

        <div className="card">
          <h3>Disk Write Speed (MB/s)</h3>
          <Line
            data={makeChart("Disk", "#f59e0b", disk)}
            options={options}
          />
        </div>

        <div className="card">
          <h3>Risk Score</h3>
          <Line
            data={makeChart("Risk", "#ef4444", risk)}
            options={options}
          />
        </div>

      </div>

      <div
        className="card"
        style={{
          marginTop: 20
        }}
      >
        <h3 style={{ marginBottom: 15 }}>System Information</h3>

        <table>
          <tbody>

            <tr>
              <td>Total Processes</td>
              <td>{latest?.process_count ?? "--"}</td>
            </tr>

            <tr>
              <td>RAM Available</td>
              <td>
                {latest
                  ? `${latest.memory_available_mb.toFixed(0)} MB`
                  : "--"}
              </td>
            </tr>

            <tr>
              <td>Sampling Interval</td>
              <td>5 Seconds</td>
            </tr>

            <tr>
              <td>CPU Temperature</td>
              <td>N/A</td>
            </tr>

          </tbody>
        </table>

      </div>

    </div>
  );
}