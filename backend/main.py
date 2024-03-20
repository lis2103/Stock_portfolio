from flask import Flask, jsonify
import requests
import oracledb
import os
from flask_cors import CORS
from flask import request, jsonify, session
from models import db, Users, Stocks
from sqlalchemy.pool import NullPool
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
CORS(app)
#oaert for communication with DB
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
app.config['JWT_SECRET_KEY'] = 'lislislis'  # Change this to a random secret key
jwt = JWTManager(app)
db.init_app(app)

# with app.app_context():
#     db.create_all()
app.secret_key = 'fbgr5jtn5r555fmkelsd'
ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'
#Finding the latest closing price for a given ticker 
def get_latest_closing_price(ticker):

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    latest_week = list(data["Weekly Time Series"].keys())[0]
    latest_close_price = data["Weekly Time Series"][latest_week]["4. close"]
    return float(latest_close_price)

#Return  the stocks of a specific  user
@app.route('/portfolio/<username>', methods=["GET"])
def get_user_portfolio(username):
    user = Users.query.filter_by(user_name=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    stocks_list = [{"ticker": stock.ticker, "quantity": stock.quantity} for stock in user.stocks.all()]
    return jsonify(stocks_list)

#percentage changess
@app.route('/<ticker>', methods=["GET"])
def get_ticker_info(ticker):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        stock_info = data.get("Weekly Time Series")
        if not stock_info:
            return jsonify({"error": "No data found for the given ticker"}), 404
        
        weeks = list(stock_info.keys())
        latest_close = float(stock_info[weeks[0]]["4. close"])
        previous_close = float(stock_info[weeks[1]]["4. close"])
        percent_change = ((latest_close - previous_close) / previous_close) * 100

        # Limit the response to the first 10 entries for readability
        limited_stock_info = {week: stock_info[week] for week in weeks[:10]}
        
        return jsonify({"stock_info": limited_stock_info, "percent_change": percent_change})
    except requests.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 500
    except Exception as err:
        return jsonify({"error": f"An error occurred: {err}"}), 500


# route for total portfolio value 
@app.route('/api/portfolio-value/<username>', methods=["GET"])
def get_portfolio_value(username):
    user = Users.query.filter_by(user_name=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        total_value = sum(get_latest_closing_price(stock.ticker) * stock.quantity for stock in user.stocks)
        return jsonify({"total_portfolio_value": total_value})
    except Exception as e:
        return jsonify({"error": f"Failed to calculate total portfolio value: {e}"}), 500
# adding stocks 
@app.route('/add-stock/<username>/<string:stock>/<int:quantity>', methods=["POST"])
def add_stock(username, stock, quantity):
    user = Users.query.filter_by(user_name=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        existing_stock = Stocks.query.filter_by(user_id=user.id, ticker=stock).first()
        if existing_stock:
            existing_stock.quantity += quantity
        else:
            new_stock = Stocks(ticker=stock, quantity=quantity, user_id=user.id)
            db.session.add(new_stock)
        db.session.commit()

        return jsonify({"message": f"{quantity} units of stock {stock} added for user {username}"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add stock: {e}"}), 500


#Removing stock
@app.route('/remove-stock/<username>/<string:stock>', methods=["DELETE"])
def remove_stock(username, stock):
    user = Users.query.filter_by(user_name=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    stock_to_remove = Stocks.query.filter_by(user_id=user.id, ticker=stock).first()
    if stock_to_remove:
        db.session.delete(stock_to_remove)
        db.session.commit()
        return jsonify({"message": f"Stock {stock} removed for user {username}"})
    else:
        return jsonify({"error": "Stock not found"}), 404


#Registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_name = data.get('user_name')
    password = data.get('password')
    email = data.get('email')

    # Check if username or email is already in use
    if Users.query.filter((Users.user_name == user_name) | (Users.email == email)).first():
        return jsonify({"error": "Username or email already in use"}), 409

    password_hash = generate_password_hash(password)  # Hash the password

    new_user = Users(user_name=user_name, password_hash=password_hash, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201



#Login a user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = Users.query.filter_by(user_name=username).first()

    if user and check_password_hash(user.password_hash, password):
        # Create JWT token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

#Logout a user
@app.route('/logout', methods=["GET"])
def logout():
    session.pop('user_id', None)  # Clears the user session
    return jsonify({"message": "Logout successful"}), 200
if __name__ == "__main__":
    app.run(debug=True)







    