import React, { useEffect, useState } from "react";

export default function Settings() {

  const [sampling, setSampling] = useState("5");
  const [warning, setWarning] = useState(60);
  const [critical, setCritical] = useState(80);

  const [email, setEmail] = useState(true);
  const [sound, setSound] = useState(true);
  const [desktop, setDesktop] = useState(true);

  const [theme, setTheme] = useState("Dark");

  useEffect(() => {

    const saved =
      JSON.parse(localStorage.getItem("pm_settings"));

    if(saved){

      setSampling(saved.sampling);
      setWarning(saved.warning);
      setCritical(saved.critical);

      setEmail(saved.email);
      setSound(saved.sound);
      setDesktop(saved.desktop);

      setTheme(saved.theme);

    }

  },[]);

  function saveSettings(){

    const settings={

      sampling,
      warning,
      critical,

      email,
      sound,
      desktop,

      theme

    };

    localStorage.setItem(
      "pm_settings",
      JSON.stringify(settings)
    );

    alert("Settings Saved Successfully");

  }

  return(

    <div>

      <h2 style={{marginBottom:20}}>
        Settings
      </h2>

      <div className="card">

        <h3>Monitoring Settings</h3>

        <br/>

        <label>
          Sampling Interval
        </label>

        <br/>

        <select
          value={sampling}
          onChange={(e)=>setSampling(e.target.value)}
        >

          <option value="5">5 Seconds</option>

          <option value="10">10 Seconds</option>

          <option value="30">30 Seconds</option>

        </select>

      </div>

      <div
        className="card"
        style={{marginTop:20}}
      >

        <h3>Risk Thresholds</h3>

        <br/>

        <label>Warning (%)</label>

        <br/>

        <input
          type="number"
          value={warning}
          onChange={(e)=>setWarning(e.target.value)}
        />

        <br/><br/>

        <label>Critical (%)</label>

        <br/>

        <input
          type="number"
          value={critical}
          onChange={(e)=>setCritical(e.target.value)}
        />

      </div>

      <div
        className="card"
        style={{marginTop:20}}
      >

        <h3>Notifications</h3>

        <br/>

        <label>

          <input
            type="checkbox"
            checked={email}
            onChange={()=>setEmail(!email)}
          />

          Email Alerts

        </label>

        <br/><br/>

        <label>

          <input
            type="checkbox"
            checked={sound}
            onChange={()=>setSound(!sound)}
          />

          Sound Alerts

        </label>

        <br/><br/>

        <label>

          <input
            type="checkbox"
            checked={desktop}
            onChange={()=>setDesktop(!desktop)}
          />

          Desktop Notifications

        </label>

      </div>

      <div
        className="card"
        style={{marginTop:20}}
      >

        <h3>Appearance</h3>

        <br/>

        <select
          value={theme}
          onChange={(e)=>setTheme(e.target.value)}
        >

          <option>Dark</option>

          <option>Light</option>

        </select>

      </div>

      <button
        onClick={saveSettings}
        style={{
          marginTop:20,
          padding:"12px 20px"
        }}
      >
        Save Settings
      </button>

    </div>

  );

}