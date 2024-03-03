
from flask import Flask, jsonify, request, render_template
import requests
import json 
import os
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
def load_portfolio_data():
    portfolio_path =  os.path.join(os.path.dirname(__file__), 'portfolio.json')
    with open(portfolio_path, 'r') as file:
        return json.load(file)

user_portfolio = load_portfolio_data()



ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'

@app.route('/')
def homepage():
    return render_template('portfolio.html')

    

@app.route('/portfolio_symbols', methods=['GET'])
def list_portfolio_symbols():
    portfolio_items = user_portfolio['portfolios'][0]['items']
    enriched_symbols = []
    total_portfolio_value = 0  # Initialize total portfolio value
    for item in portfolio_items:
        ticker = item['ticker']
        quantity = item['quantity']
        # Initialize default data
        symbol_data = {
            'ticker': ticker,
            'quantity': quantity,
            'holding_value': 0,  # Default value
            'data': {}  # Default value
        }
        weekly_data_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
        response = requests.get(weekly_data_url)
        if response.status_code == 200:
            weekly_data = response.json().get('Weekly Time Series', {})
            latest_week = next(iter(weekly_data))
            current_price = float(weekly_data[latest_week]['4. close'])
            holding_value = quantity * current_price
            total_portfolio_value += holding_value
            # Update symbol data with actual values
            symbol_data['holding_value'] = holding_value
            symbol_data['data'] = weekly_data
        # Append symbol data after if-else checks
        enriched_symbols.append(symbol_data)
    return jsonify({'total_portfolio_value': total_portfolio_value, 'stocks': enriched_symbols})



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