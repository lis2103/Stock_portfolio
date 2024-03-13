
from flask import Flask, jsonify, request, render_template
import requests
import json 
import os
from flask_cors import CORS
from sqlalchemy.pool import NullPool
import oracledb
from models import db,Stocks,Users
from werkzeug.security import generate_password_hash
import hashlib
import time



app = Flask(__name__)
CORS(app)

un = 'ADMIN'
pw = 'c!PH6i9Nk4#b3yj'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gcdcacb6a2b6a7b_gwfoqy92fsoc1x3e_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

pool = oracledb.create_pool(user=un, password=pw,
                            dsn=dsn)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+oracledb://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'creator': pool.acquire,
    'poolclass': NullPool
}

app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "VFVETDZPXW4IOBLDKK"

# I will use this if i want to create new tables
#with app.app_context():
    #db.create_all()


ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'


def load_stocks(user_id): # load all the info from the stock table

    try:
        stock_ids = Stocks.query.filter_by(user_id=user_id).with_entities(Stocks.stock_id, 
                                                                               Stocks.quantity, 
                                                                               Stocks.ticker, 
                                                                               Stocks.user_id).all()
        if stock_ids:
            return stock_ids
        else:
            return {}

    except Exception as e:
        print("Error:", str(e))



def generate_hashed_token(data):
    # Create a unique string by combining user ID, ticker, and the current timestamp
    unique_string = f"{data['user_id']}-{data['ticker']}-{time.time()}"
    
    # Generate a SHA-256 hash of the unique string
    hashed_token = hashlib.sha256(unique_string.encode()).hexdigest()
    
    return hashed_token



def single_stock_id(data): # checking for the user, and taking his portfolio datas
        with app.app_context():
            users_response = Stocks.query.filter_by(
                                        stock_id=data["stock_id"],
                                        user_id=data["user_id"],
                                        ).first()

        if users_response and users_response.stock_id:
            if data["stock_id"] == users_response.stock_id:
                response_dict = {
                    "stock_id": users_response.stock_id,
                    "ticker": users_response.ticker,
                    "user_id":users_response.user_id,
                    "quantity":users_response.quantity,
                    "action":data["action"]
                }
                return response_dict

# For the above i used prompts from chatgpt and adjust a little some points
#if you want to add more quantity of a stock, or to add a new one
def add_more(data): 
    if data["action"] == "modify":
        creation = "modify"
        new_dict = {
            "stock_id": data["stock_id"],
            "user_id": data["user_id"],
            "ticker": data["ticker"],
            "quantity": data["quantity"],
            "action": "modifiyed",
        }
    
    else:
        creation = "created"
        new_dict = {
                    "stock_id": generate_hashed_token(data),
                    "user_id": data["user_id"],
                    "ticker": data["ticker"].upper().strip(),
                    "quantity": int(data["quantity"]),
                    "action": "created",
                }
    
    #Preparing the data to make the request to the DB.
    if new_dict:
        if creation == "created":
                creation= Stocks(
                                        stock_id=new_dict["stock_id"],
                                        user_id=new_dict["user_id"],
                                        ticker=new_dict["ticker"],
                                        quantity=int(new_dict["quantity"])
                                    )
                db.session.add(creation)
                db.session.commit()
                return jsonify({"message": "The stock was sucessfully inserted"})
            
            

        if creation == "modify":
                modify =Stocks.query.filter_by(stock_id=new_dict["stock_id"],
                                                                user_id=new_dict["user_id"]
                                                            ).first()
                if modify:
                    modify.quantity = int(new_dict["quantity"])
                    db.session.commit()
                    return jsonify({"message": "Stock updated successfully"})
                else:
                    return jsonify({"message": "wrong"})   
            
    else:
        return f"Failed to modify stock"


def remove(data):# For stocks removal
        with app.app_context():
            delete = Stocks.query.filter_by(
                                    stock_id=data["stock_id"],
                                    user_id=data["user_id"],
                                    ticker=data["ticker"],
                                    quantity=int(data["quantity"])
                                ).first()
            if delete:
                db.session.delete(delete)
                db.session.commit()
                return jsonify({"message": "Stock deleted successfully"})
            else:
                return jsonify({"message": "Stock record not found"})
    



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

#This is for passing hard coded examples to the database
# def create_and_insert_user():
#     # Create a new user instance with hardcoded values
#     new_user = Users(
#         user_id='user143',  # This should be unique for each user
#         password=generate_password_hash('password123', method='sha256'),
#         user_name='John Doe',
#         email='johndoe@example.com'
#     )
#     db.session.add(new_user)  # Add the new user to the session

#     # Create hardcoded stock instances associated with the new user
#     stock1 = Stocks(
#         stock_id='stock123',  # This should be unique for each stock
#         user_id=new_user.user_id,  # Associate this stock with the newly created user
#         ticker='AAPL',
#         quantity=10
#     )

#     stock2 = Stocks(
#         stock_id='stock124',  # This should be unique for each stock
#         user_id=new_user.user_id,  # Associate this stock with the newly created user
#         ticker='GOOGL',
#         quantity=5
#     )

#     # Add the new stock entries to the session
#     db.session.add(stock1)
#     db.session.add(stock2)

#     try:
#         db.session.commit()  # Attempt to commit the session to the database
#         print("User and stocks created successfully.")
#     except Exception as e:
#         db.session.rollback()  # Roll back the session in case of error
#         print(f"Failed to create user and stocks: {e}")


if __name__ == '__main__':
    # with app.app_context():
    #     create_and_insert_user()
    app.run(debug=True)




    