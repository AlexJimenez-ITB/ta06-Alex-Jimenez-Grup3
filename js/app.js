document.addEventListener('DOMContentLoaded', function() {
    fetch('data/precipitation_summary.csv')
        .then(response => response.text())
        .then(data => {
            const rows = data.split('\n').slice(1);
            const statistics = calculateStatistics(rows);
            displayStatistics(statistics);
            createChart(rows);
            document.getElementById('exportBtn').addEventListener('click', () => exportToCSV(statistics));
        });
});

function calculateStatistics(rows) {
    let totalPrecipitation = 0;
    let medianPrecipitation = 0;
    let count = 0;
    rows.forEach(row => {
        const cols = row.split(',');
        if (cols.length === 3 && parseFloat(cols[0]) >= 2006 && parseFloat(cols[0]) <= 2100) {
            totalPrecipitation += parseFloat(cols[1]);
            medianPrecipitation += parseFloat(cols[2]);
            count++;
        }
    });
    return {
        totalPrecipitation: totalPrecipitation / count,
        medianPrecipitation: medianPrecipitation / count
    };
}

function displayStatistics(statistics) {
    const statisticsDiv = document.getElementById('statistics');
    statisticsDiv.innerHTML = `
        <p>Precipitación Total Promedio: ${isNaN(statistics.totalPrecipitation) ? 'NaN' : statistics.totalPrecipitation.toFixed(2)}</p>
        <p>Precipitación Mediana Promedio: ${isNaN(statistics.medianPrecipitation) ? 'NaN' : statistics.medianPrecipitation.toFixed(2)}</p>
    `;
}

function exportToCSV(statistics) {
    const csvContent = `data:text/csv;charset=utf-8,Precipitación Total Promedio,Precipitación Mediana Promedio\n${statistics.totalPrecipitation.toFixed(2)},${statistics.medianPrecipitation.toFixed(2)}`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'statistics_summary.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}