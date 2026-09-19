const historyElement = document.getElementById("history-data");

const historyData = JSON.parse(historyElement.textContent);

// ===============================
// SUMMARY CARDS
// ===============================

// Total number of predictions
const totalPredictions = historyData.length;

document.getElementById("totalPredictions").textContent = totalPredictions;


// Average Previous SGPA
const sgpaValues = historyData
    .map(record => parseFloat(record.previous_sgpa))
    .filter(value => !isNaN(value));

let averageSGPA = 0;

if (sgpaValues.length > 0) {
    const totalSGPA = sgpaValues.reduce((sum, value) => sum + value, 0);
    averageSGPA = totalSGPA / sgpaValues.length;
}

document.getElementById("averageSGPA").textContent =
    averageSGPA.toFixed(2);


// Latest Prediction
if (historyData.length > 0) {

    // Sort records by created_at
    const sortedHistory = [...historyData].sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
    );

    const latestPrediction = sortedHistory[0].prediction;

    document.getElementById("latestPrediction").textContent =
        latestPrediction;
}


    const labels = historyData.map(record => {
        return new Date(record.created_at).toLocaleDateString();
    });

    const sgpaData = historyData.map(record => {
        return parseFloat(record.previous_sgpa);
    });

    const ctx = document.getElementById("sgpaChart");

    new Chart(ctx, {
        type: "line",

        data: {
            labels: labels,

            datasets: [{
                label: "Previous SGPA",
                data: sgpaData,
                borderWidth: 2,
                tension: 0.3,
                fill: false
            }]
        },

        options: {
            responsive: true,

            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: "SGPA"
                    }
                },

                x: {
                    title: {
                        display: true,
                        text: "Prediction Date"
                    }
                }
            }
        }
    });


const attendanceData = historyData.map(record => {
    return parseFloat(record.attendance_percentage);
});


const attendanceCtx = document.getElementById("attendanceChart");

new Chart(attendanceCtx, {
    type: "bar",

    data: {
        labels: labels,

        datasets: [{
            label: "Attendance Percentage",
            data: attendanceData,
            borderWidth: 1
        }]
    },

    options: {
        responsive: true,

        scales: {
            y: {
                beginAtZero: true,
                min: 0,
                max: 100,

                title: {
                    display: true,
                    text: "Attendance (%)"
                }
            },

            x: {
                title: {
                    display: true,
                    text: "Prediction Date"
                }
            }
        }
    }
});


// Count prediction categories
const predictionCounts = {};

historyData.forEach(record => {
    const prediction = record.prediction;

    predictionCounts[prediction] =
        (predictionCounts[prediction] || 0) + 1;
});

// Create prediction chart
const predictionCtx = document.getElementById("predictionChart");

new Chart(predictionCtx, {
    type: "doughnut",

    data: {
        labels: Object.keys(predictionCounts),

        datasets: [{
            label: "Prediction Distribution",
            data: Object.values(predictionCounts),
            borderWidth: 1
        }]
    },

    options: {
        responsive: true,

        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }
});