
from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

# Dummy user portfolio for demonstration
user_portfolio = {
    "user_id": "PANTELIS",
    "user_name": "VR13",
    "portfolios": [
        {
            "portfolio_id": "portfolio1",
            "items": [
                {"ticker": "AAPL", "quantity": 10, "purchase_price": 180},
                {"ticker": "GOOGL", "quantity": 5, "purchase_price": 2700},
            ]
        }
    ]
}



# Replace 'YOUR_API_KEY' with your actual AlphaVantage API key
ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'

@app.route('/')
def homepage():
    return render_template('portfolio.html')

    

@app.route('/portfolio_symbols', methods=['GET'])
def list_portfolio_symbols():
    # Assuming a single portfolio for simplicity
    portfolio_items = user_portfolio['portfolios'][0]['items']
    enriched_symbols = []
    for item in portfolio_items:
        ticker = item['ticker']
        quantity = item['quantity']
        # Fetch the weekly data for each symbol (you may want to limit this to not hit rate limits)
        weekly_data_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
        response = requests.get(weekly_data_url)
        if response.status_code == 200:
            weekly_data = response.json().get('Weekly Time Series', {})
        else:
            weekly_data = {}
        enriched_symbols.append({
            'ticker': ticker,
            'quantity': quantity,
            'data': weekly_data
        })
    return jsonify(enriched_symbols)


@app.route('/weekly_series/<ticker>', methods=['GET'])
def get_weekly_series(ticker):
    datatype = request.args.get('datatype', 'json')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&datatype={datatype}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        # Extract the "Weekly Time Series" part of the response
        time_series_weekly = data.get('Weekly Time Series', {})
        return jsonify({
            'symbol': ticker,
            'data': time_series_weekly
        })
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code
   
  

if __name__ == '__main__': 
    app.run(debug=True)