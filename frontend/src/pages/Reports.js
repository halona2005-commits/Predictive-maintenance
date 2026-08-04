import React, { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function Reports() {

  const [history, setHistory] = useState([]);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  async function loadData() {
    try {
      const res = await fetch(`${API}/history`);
      const data = await res.json();
      setHistory(data.metrics || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const filtered = useMemo(() => {

    return history.filter(item => {

      const d = new Date(item.timestamp);

      if (fromDate && d < new Date(fromDate))
        return false;

      if (toDate) {
        const end = new Date(toDate);
        end.setHours(23,59,59,999);

        if (d > end)
          return false;
      }

      return true;

    });

  }, [history, fromDate, toDate]);

  const totalPredictions = filtered.length;

  const anomalies = filtered.filter(
    x => x.cpu_percent > 80 || x.memory_percent > 85
  ).length;

  const healthy = totalPredictions - anomalies;

  const accuracy =
    totalPredictions === 0
      ? 0
      : ((healthy / totalPredictions) * 100).toFixed(1);

  const avgCPU =
    totalPredictions === 0
      ? 0
      : (
          filtered.reduce((a,b)=>a+b.cpu_percent,0)
          / totalPredictions
        ).toFixed(1);

  const avgMemory =
    totalPredictions === 0
      ? 0
      : (
          filtered.reduce((a,b)=>a+b.memory_percent,0)
          / totalPredictions
        ).toFixed(1);

  const avgDisk =
    totalPredictions === 0
      ? 0
      : (
          filtered.reduce((a,b)=>a+b.disk_write_mbps,0)
          / totalPredictions
        ).toFixed(2);

  function downloadCSV(){

    let csv =
      "Timestamp,CPU,Memory,Disk Write\n";

    filtered.forEach(r=>{

      csv +=
        `${r.timestamp},${r.cpu_percent},${r.memory_percent},${r.disk_write_mbps}\n`;

    });

    const blob =
      new Blob([csv],{
        type:"text/csv"
      });

    const url =
      URL.createObjectURL(blob);

    const a =
      document.createElement("a");

    a.href=url;

    a.download="predictive_report.csv";

    a.click();

    URL.revokeObjectURL(url);

  }

  return(

    <div>

      <h2 style={{marginBottom:20}}>
        Reports
      </h2>

      <div
        className="card"
        style={{
          display:"flex",
          gap:20,
          marginBottom:20
        }}
      >

        <div>

          <label>From</label>

          <br/>

          <input
            type="date"
            value={fromDate}
            onChange={(e)=>
              setFromDate(e.target.value)
            }
          />

        </div>

        <div>

          <label>To</label>

          <br/>

          <input
            type="date"
            value={toDate}
            onChange={(e)=>
              setToDate(e.target.value)
            }
          />

        </div>

        <button
          style={{height:40,marginTop:20}}
          onClick={loadData}
        >
          Generate Report
        </button>

      </div>

      <div
        style={{
          display:"grid",
          gridTemplateColumns:"repeat(4,1fr)",
          gap:20
        }}
      >

        <div className="card">
          <h4>Total Predictions</h4>
          <h2>{totalPredictions}</h2>
        </div>

        <div className="card">
          <h4>Anomalies</h4>
          <h2>{anomalies}</h2>
        </div>

        <div className="card">
          <h4>Healthy Sessions</h4>
          <h2>{healthy}</h2>
        </div>

        <div className="card">
          <h4>Accuracy</h4>
          <h2>{accuracy}%</h2>
        </div>

      </div>

      <div
        className="card"
        style={{
          marginTop:20
        }}
      >

        <h3>Average Statistics</h3>

        <table
          style={{
            marginTop:15
          }}
        >

          <tbody>

            <tr>
              <td>Average CPU Usage</td>
              <td>{avgCPU}%</td>
            </tr>

            <tr>
              <td>Average Memory Usage</td>
              <td>{avgMemory}%</td>
            </tr>

            <tr>
              <td>Average Disk Write</td>
              <td>{avgDisk} MB/s</td>
            </tr>

            <tr>
              <td>Average Response Time</td>
              <td>5 Seconds</td>
            </tr>

          </tbody>

        </table>

      </div>

      <div
        style={{
          display:"flex",
          gap:20,
          marginTop:20
        }}
      >

        <button
          onClick={()=>
            window.print()
          }
        >
          Download PDF
        </button>

        <button
          onClick={downloadCSV}
        >
          Download CSV
        </button>

      </div>

    </div>

  );

}