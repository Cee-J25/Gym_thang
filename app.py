from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import time
import threading
from twilio.rest import Client

app = Flask(__name__)

# Configuration
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'
WHATSAPP_NUMBER = 'whatsapp:+27638266433'  # Default number

# Mock data storage (in a real app, use a database)
user_settings = {
    'whatsapp_notifications': True,
    'whatsapp_number': '0638266433'
}

market_data = {
    'gold': {
        'prices': [],
        'timestamps': [],
        'trend_lines': []
    },
    'usdjpy': {
        'prices': [],
        'timestamps': [],
        'trend_lines': []
    }
}

# Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def fetch_market_data(market):
    """Fetch market data from an API (mock implementation)"""
    # In a real application, you would fetch from a financial API like Alpha Vantage, OANDA, etc.
    now = datetime.now()
    prices = []
    timestamps = []
    
    # Generate mock data
    base_price = 1800 if market == 'gold' else 110.0
    volatility = 15 if market == 'gold' else 1.5
    
    for i in range(100):
        price = base_price + volatility * (0.5 - (i % 20)/20)
        prices.append(price)
        timestamps.append((now - timedelta(minutes=100-i)).strftime('%H:%M'))
    
    return prices, timestamps

def analyze_trend(prices):
    """Perform trendline analysis"""
    # Simplified trend analysis - in a real app, use proper technical analysis
    touch_count = 0
    trend = 'neutral'
    description = "No strong trend detected"
    
    if len(prices) < 10:
        return {
            'trend': trend,
            'description': description,
            'touch_count': touch_count
        }
    
    # Check for higher lows (bullish)
    last_quarter = prices[-len(prices)//4:]
    if all(last_quarter[i] > last_quarter[i-1] for i in range(1, len(last_quarter))):
        trend = 'bullish'
        description = "Higher lows detected - Bullish trend"
        touch_count = 3  # Mock value
    
    # Check for lower highs (bearish)
    elif all(last_quarter[i] < last_quarter[i-1] for i in range(1, len(last_quarter))):
        trend = 'bearish'
        description = "Lower highs detected - Bearish trend"
        touch_count = 2  # Mock value
    
    return {
        'trend': trend,
        'description': description,
        'touch_count': touch_count
    }

def check_for_alerts():
    """Periodically check for alerts and send notifications"""
    while True:
        for market in ['gold', 'usdjpy']:
            prices, _ = fetch_market_data(market)
            analysis = analyze_trend(prices)
            
            if analysis['touch_count'] >= 2 and user_settings['whatsapp_notifications']:
                send_whatsapp_alert(market, analysis)
        
        time.sleep(60 * 15)  # Check every 15 minutes

def send_whatsapp_alert(market, analysis):
    """Send WhatsApp alert"""
    market_name = "Gold (XAU/USD)" if market == 'gold' else "USD/JPY"
    message = (
        f"ALERT: {market_name}\n"
        f"Trend: {analysis['trend'].upper()}\n"
        f"Trendline touched {analysis['touch_count']} times\n"
        f"Analysis: {analysis['description']}"
    )
    
    try:
        twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:{user_settings["whatsapp_number"]}'
        )
        print(f"Alert sent for {market}")
    except Exception as e:
        print(f"Failed to send alert: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_market_data')
def get_market_data():
    market = request.args.get('market', 'gold')
    prices, timestamps = fetch_market_data(market)
    analysis = analyze_trend(prices)
    
    # Generate historical trends (mock data)
    historical_trends = []
    for i in range(5):
        historical_trends.append({
            'date': (datetime.now() - timedelta(days=i)).isoformat(),
            'trend': 'bullish' if i % 2 == 0 else 'bearish',
            'touch_count': 2 if i % 2 == 0 else 3,
            'notes': f"Sample trend pattern from {i+1} day(s) ago"
        })
    
    return jsonify({
        'prices': prices,
        'timestamps': timestamps,
        'trend_analysis': analysis,
        'historical_trends': historical_trends
    })

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    user_settings['whatsapp_notifications'] = data.get('whatsapp_notifications', True)
    user_settings['whatsapp_number'] = data.get('whatsapp_number', '0638266433')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Start the alert thread
    alert_thread = threading.Thread(target=check_for_alerts, daemon=True)
    alert_thread.start()
    
    app.run(debug=True)