import React from "react";

function HealthCard({health}) {

    let status = "Healthy";
    let color = "#4ade80";

    if(health < 50){
        status="Critical";
        color="#ef4444";
    }
    else if(health < 75){
        status="Warning";
        color="#f59e0b";
    }


    return (

        <div style={{
            background:"#131720",
            border:"1px solid #232838",
            borderRadius:12,
            padding:"18px"
        }}>

            <div style={{
                color:"#64748b",
                fontSize:11,
                textTransform:"uppercase"
            }}>
                System Health
            </div>


            <div style={{
                fontSize:50,
                fontWeight:800,
                color,
                marginTop:10
            }}>
                {health}%
            </div>


            <div style={{
                color,
                fontSize:13
            }}>
                ● {status}
            </div>

        </div>

    );

}

export default HealthCard;