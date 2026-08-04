import React, { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";
const PAGE_SIZE = 20;

export default function History() {

  const [history, setHistory] = useState([]);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [page, setPage] = useState(1);

  async function loadHistory() {
    try {
      const res = await fetch(`${API}/history`);
      const data = await res.json();
      setHistory(data.metrics || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {

    loadHistory();

    const timer = setInterval(loadHistory, 30000);

    return () => clearInterval(timer);

  }, []);

  const filtered = useMemo(() => {

    return history.filter(item => {

      const date = new Date(item.timestamp);

      if (fromDate && date < new Date(fromDate))
        return false;

      if (toDate) {

        const end = new Date(toDate);
        end.setHours(23,59,59,999);

        if (date > end)
          return false;

      }

      return true;

    });

  }, [history, fromDate, toDate]);

  const totalPages = Math.max(
    1,
    Math.ceil(filtered.length / PAGE_SIZE)
  );

  const current = filtered.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  return (

    <div>

      <h2 style={{ marginBottom: 20 }}>
        History
      </h2>

      <div
        className="card"
        style={{
          marginBottom:20,
          display:"flex",
          gap:20,
          alignItems:"center"
        }}
      >

        <div>

          <label>From</label>

          <br/>

          <input
            type="date"
            value={fromDate}
            onChange={(e)=>{

              setFromDate(e.target.value);
              setPage(1);

            }}
          />

        </div>

        <div>

          <label>To</label>

          <br/>

          <input
            type="date"
            value={toDate}
            onChange={(e)=>{

              setToDate(e.target.value);
              setPage(1);

            }}
          />

        </div>

      </div>

      <div className="card">

        <table>

          <thead>

            <tr>

              <th>Time</th>
              <th>CPU %</th>
              <th>Memory %</th>
              <th>Disk MB/s</th>
              <th>Prediction</th>
              <th>Fault</th>
              <th>Severity</th>

            </tr>

          </thead>

          <tbody>

            {current.map((row)=>(

              <tr key={row.id}>

                <td>
                  {new Date(row.timestamp).toLocaleString()}
                </td>

                <td>
                  {row.cpu_percent.toFixed(1)}
                </td>

                <td>
                  {row.memory_percent.toFixed(1)}
                </td>

                <td>
                  {row.disk_write_mbps.toFixed(2)}
                </td>

                <td>

                  {(row.cpu_percent > 80 ||
                    row.memory_percent > 85)
                    ? "Anomaly Detected"
                    : "Normal"}

                </td>

                <td>

                  {row.cpu_percent > 80
                    ? "CPU"
                    : row.memory_percent > 85
                    ? "Memory"
                    : "Normal"}

                </td>

                <td>

                  {row.cpu_percent > 80
                    ? "HIGH"
                    : row.memory_percent > 85
                    ? "MEDIUM"
                    : "LOW"}

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

      <div
        style={{
          display:"flex",
          justifyContent:"center",
          gap:10,
          marginTop:20
        }}
      >

        <button
          disabled={page===1}
          onClick={()=>setPage(page-1)}
        >
          Previous
        </button>

        <span
          style={{
            padding:"8px 15px"
          }}
        >
          Page {page} / {totalPages}
        </span>

        <button
          disabled={page===totalPages}
          onClick={()=>setPage(page+1)}
        >
          Next
        </button>

      </div>

    </div>

  );

}