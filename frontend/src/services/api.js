const API_URL = "http://127.0.0.1:8000";


export async function getPrediction(){

    try {

        const response = await fetch(
            `${API_URL}/predict`
        );


        if(!response.ok){
            throw new Error("Prediction API failed");
        }


        return await response.json();


    } catch(error){

        console.error(
            "API Error:",
            error
        );

        throw error;
    }
}