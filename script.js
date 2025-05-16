document.addEventListener('DOMContentLoaded', function() {
    let currentMarket = 'gold';
    let marketChart = null;
    const whatsappNumber = document.getElementById('whatsapp-number');
    const notificationCheckbox = document.getElementById('whatsapp-notifications');
    
    // Initialize chart
    initChart();
    
    // Market selector buttons
    document.getElementById('gold-btn').addEventListener('click', function() {
        currentMarket = 'gold';
        updateActiveButton('gold-btn');
        fetchMarketData();
    });
    
    document.getElementById('usdjpy-btn').addEventListener('click', function() {
        currentMarket = 'usdjpy';
        updateActiveButton('usdjpy-btn');
        fetchMarketData();
    });
    
    // Save settings
    document.getElementById('save-settings').addEventListener('click', function() {
        const enabled = notificationCheckbox.checked;
        const number = whatsappNumber.value;
        
        fetch('/update_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                whatsapp_notifications: enabled,
                whatsapp_number: number
            })
        }).then(response => response.json())
        .then(data => {
            alert('Settings updated successfully!');
        });
    });
    
    // Initial data fetch
    fetchMarketData();
    
    function updateActiveButton(activeId) {
        document.getElementById('gold-btn').classList.remove('active');
        document.getElementById('usdjpy-btn').classList.remove('active');
        document.getElementById(activeId).classList.add('active');
    }
    
    function initChart() {
        const ctx = document.getElementById('market-chart').getContext('2d');
        marketChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Price',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Market Price Chart'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price'
                        }
                    }
                }
            }
        });
    }
    
    function fetchMarketData() {
        fetch(`/get_market_data?market=${currentMarket}`)
            .then(response => response.json())
            .then(data => {
                updateChart(data.prices, data.timestamps);
                updateTrendAnalysis(data.trend_analysis);
                updateHistoricalTrends(data.historical_trends);
            });
    }
    
    function updateChart(prices, timestamps) {
        marketChart.data.labels = timestamps;
        marketChart.data.datasets[0].data = prices;
        marketChart.data.datasets[0].label = currentMarket === 'gold' ? 'Gold (XAU/USD)' : 'USD/JPY';
        marketChart.update();
    }
    
    function updateTrendAnalysis(analysis) {
        const trendStatus = document.getElementById('trend-status');
        
        let html = `<h3>Current Trend: <span class="${analysis.trend}">${analysis.trend.toUpperCase()}</span></h3>`;
        html += `<p>${analysis.description}</p>`;
        
        if (analysis.touch_count > 1) {
            html += `<p class="alert">Trendline touched ${analysis.touch_count} times!</p>`;
        }
        
        trendStatus.innerHTML = html;
    }
    
    function updateHistoricalTrends(trends) {
        const trendsContainer = document.getElementById('trend-patterns');
        let html = '<div class="trend-grid">';
        
        trends.forEach(trend => {
            html += `
                <div class="trend-item">
                    <h4>${new Date(trend.date).toLocaleDateString()}</h4>
                    <p>Type: <span class="${trend.trend}">${trend.trend.toUpperCase()}</span></p>
                    <p>Touch Count: ${trend.touch_count}</p>
                    <p>${trend.notes}</p>
                </div>
            `;
        });
        
        html += '</div>';
        trendsContainer.innerHTML = html;
    }
});