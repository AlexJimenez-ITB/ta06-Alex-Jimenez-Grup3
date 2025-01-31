function createChart(rows) {
    const labels = [];
    const data = [];
    rows.forEach(row => {
        const cols = row.split(',');
        const year = parseFloat(cols[0]);
        if (cols.length === 3 && year >= 2006 && year <= 2100) {
            labels.push(year);
            data.push(parseFloat(cols[1]));
        }
    });

    const ctx = document.getElementById('precipitationChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Precipitación Total',
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Año'
                    },
                    type: 'linear',
                    position: 'bottom',
                    ticks: {
                        stepSize: 1
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Precipitación Total'
                    }
                }
            }
        }
    });

    // Export chart as image
    const image = chart.toBase64Image();
    const imgElement = document.getElementById('summaryImage');
    imgElement.src = image;
}