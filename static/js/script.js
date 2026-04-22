/* ===============================
   GLOBAL INCIDENT MAP
================================ */

const map = L.map('map').setView([20, 0], 2);

L.tileLayer(
'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
{
    attribution: '© OpenStreetMap contributors'
}).addTo(map);


/* ===============================
   LOAD INCIDENT DATA
================================ */

fetch('/api/map_data')
.then(res => res.json())
.then(data => {

    data.forEach(crash => {

        let color =
            crash.Survival_Rate > 0.8 ? '#00f3ff' :
            crash.Survival_Rate > 0.5 ? '#ffe600' :
            '#ff0055';


        const marker = L.circleMarker(
            [crash.Latitude, crash.Longitude],
            {
                radius: 4,
                fillColor: color,
                color: "transparent",
                fillOpacity: 0.8
            }
        ).addTo(map);


        /* TOOLTIP INFORMATION */

        marker.bindTooltip(

        `
        <b>Aircraft:</b> ${crash.Make}<br>
        <b>Survival Rate:</b> ${(crash.Survival_Rate * 100).toFixed(1)}%<br>
        <b>Latitude:</b> ${crash.Latitude}<br>
        <b>Longitude:</b> ${crash.Longitude}
        `,

        {
            direction: "top",
            offset: [0,-5],
            opacity: 0.9
        }

        );

    });

});


/* ===============================
   PIE CHART INITIALIZATION
================================ */

const chartContext = document.getElementById("pieChart");

let pieChart = new Chart(chartContext, {

    type: "doughnut",

    data: {
        labels: ["Critical Risk", "Moderate Risk", "Safe"],

        datasets: [{
            data: [33,33,34],
            backgroundColor: [
                "#ff0055",
                "#ffe600",
                "#00f3ff"
            ],
            borderWidth: 0
        }]
    },

    options: {
        responsive: true,
        plugins: {
            legend: {
                position: "right",
                labels: {
                    color: "#ffffff"
                }
            }
        }
    }

});


function updatePieChart(values){

    pieChart.data.datasets[0].data = values;
    pieChart.update();

}


/* ===============================
   LOTTIE ANIMATION
================================ */

let currentAnimation = null;

function loadLottieAnimation(type){

    if(currentAnimation){
        currentAnimation.destroy();
    }

    let animationPath = "";

    if(type === "safe"){
        animationPath = "/static/lottie/safe.json";
    }
    else if(type === "moderate"){
        animationPath = "/static/lottie/moderate.json";
    }
    else{
        animationPath = "/static/lottie/danger.json";
    }

    currentAnimation = lottie.loadAnimation({
        container: document.getElementById("lottieContainer"),
        renderer: "svg",
        loop: true,
        autoplay: true,
        path: animationPath
    });

}


/* ===============================
   FORM SUBMIT (PREDICTION)
================================ */

const form = document.getElementById("predictionForm");

form.addEventListener("submit", async function(e){

    e.preventDefault();

    const payload = {
        make: document.getElementById("make").value,
        phase: document.getElementById("phase").value,
        weather: document.getElementById("weather").value,
        engines: document.getElementById("engines").value,
        month: document.getElementById("month").value
    };

    const response = await fetch("/api/predict",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(payload)
    });

    const data = await response.json();

    if(!data.success) return;


    /* SHOW LOADING ANIMATION */

    document.getElementById("loadingOverlay").style.display="flex";

    let mode = "safe";

    if(data.safety_score < 50){
        mode = "danger";
    }
    else if(data.safety_score < 80){
        mode = "moderate";
    }

    loadLottieAnimation(mode);

    if (window.triggerBackground) {
        triggerBackground(mode);
    }


    /* REDIRECT TO RESULT PAGE */

    setTimeout(()=>{

        let advice="";

        if(mode === "safe"){
            advice="Aircraft operating conditions indicate high survivability.";
        }
        else if(mode === "moderate"){
            advice="Moderate turbulence risk detected. Monitoring recommended.";
        }
        else{
            advice="Critical safety risk detected. Immediate mitigation required.";
        }

        const url =
            "/result?"
            + "score=" + data.safety_score
            + "&risk=" + encodeURIComponent(data.risk_level)
            + "&critical=" + data.breakdown.critical
            + "&moderate=" + data.breakdown.moderate
            + "&safe=" + data.breakdown.safe
            + "&suggestion=" + encodeURIComponent(advice);

        window.location.href = url;

    },2500);

});
particlesJS("particles-js", {

    particles: {

        number: {
            value: 80
        },

        color: {
            value: "#00f3ff"
        },

        shape: {
            type: "circle"
        },

        opacity: {
            value: 0.4
        },

        size: {
            value: 2
        },

        move: {
            enable: true,
            speed: 0.6,
            direction: "none",
            out_mode: "out"
        }

    },

    interactivity: {
        detect_on: "canvas",
        events: {
            onhover: {
                enable: false
            }
        }
    },

    retina_detect: true

});