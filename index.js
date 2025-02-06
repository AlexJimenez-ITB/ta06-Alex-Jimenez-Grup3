function showImage(imageId) {
    const imageMap = {
        'precipitation_trend': 'output/precipitation_trend.png',
        'annual_variation_rate': 'output/annual_variation_rate.png',
        'precipitation_distribution': 'output/precipitation_distribution.png',
        'extreme_years': 'output/extreme_years.png',
        'precipitation_variability': 'output/precipitation_variability.png'
    };

    const summaryImage = document.getElementById('summaryImage');
    summaryImage.src = imageMap[imageId];
}