
from flask import Flask, jsonify, request, session,redirect
import requests
import json 
import os
from flask_cors import CORS
from sqlalchemy.pool import NullPool
import oracledb
from models import db,Stocks,Users
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token



app = Flask(__name__)
app.secret_key = '156673d0aadd4b35e899d59664edd52f'
CORS(app)

un = 'ADMIN'
pw = 'c!PH6i9Nk4#b3yj'
dsn = '((description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gcdcacb6a2b6a7b_gwfoqy92fsoc1x3e_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'
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



# I will use this if i want to create new tables
#with app.app_context():
    #db.create_all()



#fuction for taking all the data from the API for a specific stock
def get_latest_closing_price(ticker):
    ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    last_week = list(data["Weekly Time Series"].keys())[0]
    closing_price = data["Weekly Time Series"][last_week]["4. close"]
    return float(closing_price)

#Returns all the stock for a selected user 
@app.route('/portfolio/<username>', methods=["GET"])
def homepage(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        stocks_list = [
            {
                "ticker": stock.ticker,
                "quantity": stock.quantity
            } for stock in user.stocks.all()
        ]
        return jsonify(stocks_list)
    return jsonify({"message": "The user does not exist"}), 404

# TSW of a stock
@app.route('/<ticker>', methods=["GET"])
def ticker_info(ticker):
    try:
        ALPHA_VANTAGE_API_KEY = '6NBLKRHSKPUYOROW'
        stock = ticker
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock}&apikey={ALPHA_VANTAGE_API_KEY}"
        
        #  Getting stock information
        response = requests.get(url)
        data = response.json()
        stock_info = data["Weekly Time Series"]
        selected_items = list(stock_info.items())[:10]
        stock_info = dict(selected_items)
        
        # Percentage change 
        last_week_key = list(stock_info.keys())[0]
        previous_week_key = list(stock_info.keys())[1]
        latest_close = float(stock_info[last_week_key]["4. close"])
        previous_close = float(stock_info[previous_week_key]["4. close"])
        percentage_change = ((latest_close - previous_close) / previous_close) * 100
        
        return jsonify({"stock_information": stock_info, "percentage_change": percentage_change})

    except Exception as e:
        print(str(e))
        return {"error": "Failed to retrieve ticker information"}, 500

# Total portfolio value
@app.route('/total-portfolio-value/<username>', methods=["GET"])
def total_portfolio_value(username):
    user = Users.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not exist"}), 404

    if user.stocks.count() == 0:
        return jsonify({"error": "User has 0 stocks"}), 404

    total_value = 0
    for stock in user.stocks.all():  
        try:
            latest_close_price = get_latest_closing_price(stock.ticker)
            total_value += latest_close_price * stock.quantity
        except Exception as e:
            continue  
    
    return jsonify({"total_portfolio_value": total_value})

#Add  stock to a  portfolio
@app.route('/add-stock/<username>/<string:stock>/<int:quantity>', methods=["POST"])
def add_stock(username, stock, quantity):
    user = Users.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not exist"}), 404
    previous_stock = Stocks.query.filter_by(user_id=user.id, ticker=stock).first()
    if previous_stock:
        previous_stock.quantity += quantity
    else:
        new_stock = Stocks(ticker=stock, quantity=quantity, user_id=user.id)
        db.session.add(new_stock)
    db.session.commit()
    return jsonify({"message": f"{quantity}  of {stock} stocks added for  {username}"})

#Remove stock 
@app.route('/remove-stock/<string:username>/<string:stock>', methods=["DELETE"])
def remove_stock(username, stock):
    user = Users.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not exist"}), 404

    stock_to_remove = Stocks.query.filter_by(user_id=user.id, ticker=stock).first()
    if stock_to_remove:
        db.session.delete(stock_to_remove)
        db.session.commit()
        return jsonify({"message": f"Stock {stock} removed"})
    else:
        return jsonify({"error": "Stock not found"}), 404

#Create a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if Users.query.filter_by(username=username).first():
        return jsonify({"error": "Username exist"}), 409

    hashed_password = generate_password_hash(password)
    new_user = Users(username=username, password_hash=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered "}), 201

#Login 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = Users.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id  
        return jsonify({"message": " Successful Login "}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

#Logout 
@app.route('/logout', methods=["GET"])
def logout():
    session.pop('user_id', None) 
    return jsonify({"message": "Logout successful"}), 200

if __name__ == "__main__":
    app.run(debug=True)


# def load_stocks(user_id): # load all the info from the stock table

#     try:
#         stock_ids = Stocks.query.filter_by(user_id=user_id).with_entities(Stocks.stock_id, 
#                                                                                Stocks.quantity, 
#                                                                                Stocks.ticker, 
#                                                                                Stocks.user_id).all()
#         if stock_ids:
#             return stock_ids
#         else:
#             return {}

#     except Exception as e:
#         print("Error:", str(e))



# def generate_hashed_token(data):
#     # Create a unique string by combining user ID, ticker, and the current timestamp
#     unique_string = f"{data['user_id']}-{data['ticker']}-{time.time()}"
    
#     # Generate a SHA-256 hash of the unique string
#     hashed_token = hashlib.sha256(unique_string.encode()).hexdigest()
    
#     return hashed_token



# def single_stock_id(data): # checking for the user, and taking his portfolio datas
#         with app.app_context():
#             users_response = Stocks.query.filter_by(
#                                         stock_id=data["stock_id"],
#                                         user_id=data["user_id"],
#                                         ).first()

#         if users_response and users_response.stock_id:
#             if data["stock_id"] == users_response.stock_id:
#                 response_dict = {
#                     "stock_id": users_response.stock_id,
#                     "ticker": users_response.ticker,
#                     "user_id":users_response.user_id,
#                     "quantity":users_response.quantity,
#                     "action":data["action"]
#                 }
#                 return response_dict

# # For the above i used prompts from chatgpt and adjust a little some points
# #if you want to add more quantity of a stock, or to add a new one
# def add_more(data): 
#     if data["action"] == "modify":
#         creation = "modify"
#         new_dict = {
#             "stock_id": data["stock_id"],
#             "user_id": data["user_id"],
#             "ticker": data["ticker"],
#             "quantity": data["quantity"],
#             "action": "modifiyed",
#         }
    
#     else:
#         creation = "created"
#         new_dict = {
#                     "stock_id": generate_hashed_token(data),
#                     "user_id": data["user_id"],
#                     "ticker": data["ticker"].upper().strip(),
#                     "quantity": int(data["quantity"]),
#                     "action": "created",
#                 }
    
#     #Preparing the data to make the request to the DB.
#     if new_dict:
#         if creation == "created":
#                 creation= Stocks(
#                                         stock_id=new_dict["stock_id"],
#                                         user_id=new_dict["user_id"],
#                                         ticker=new_dict["ticker"],
#                                         quantity=int(new_dict["quantity"])
#                                     )
#                 db.session.add(creation)
#                 db.session.commit()
#                 return jsonify({"message": "The stock was sucessfully inserted"})
            
            

#         if creation == "modify":
#                 modify =Stocks.query.filter_by(stock_id=new_dict["stock_id"],
#                                                                 user_id=new_dict["user_id"]
#                                                             ).first()
#                 if modify:
#                     modify.quantity = int(new_dict["quantity"])
#                     db.session.commit()
#                     return jsonify({"message": "Stock updated successfully"})
#                 else:
#                     return jsonify({"message": "wrong"})   
            
#     else:
#         return f"Failed to modify stock"


# def remove(data):# For stocks removal
#         with app.app_context():
#             delete = Stocks.query.filter_by(
#                                     stock_id=data["stock_id"],
#                                     user_id=data["user_id"],
#                                     ticker=data["ticker"],
#                                     quantity=int(data["quantity"])
#                                 ).first()
#             if delete:
#                 db.session.delete(delete)
#                 db.session.commit()
#                 return jsonify({"message": "Stock deleted successfully"})
#             else:
#                 return jsonify({"message": "Stock record not found"})
    




# @app.route('/<user>', methods=["GET"])
# def homepage(user):
#     print(f"Fetching stocks for user: {user}")
#     user_id = user
#     client_stocks = load_stocks(user_id)
#     if client_stocks:
#         print(f"Found stocks for user {user}: {client_stocks}")
#     if client_stocks:
#         print(f"Found stocks for user {user}: {client_stocks}")
#         stock_dict = {}
#         total_value = 0

#         for item in client_stocks:
#             stock = item[2]

#             weekly_data_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock}&apikey={ALPHA_VANTAGE_API_KEY}'
#             response = requests.get(weekly_data_url)
#             data = response.json()
#             if 'Weekly Time Series' in data:
#                 # Find the latest week's data
#                 latest_week = max(data['Weekly Time Series'].keys())
#                 latest_data = data['Weekly Time Series'][latest_week]
#                 closing_price = float(latest_data['4. close'])
#                 stock_dict[item[2]] = {
#                     "stock_id": item[0],
#                     "quantity": item[1],
#                     "price": closing_price,
#                     "latest_trading_day": latest_week,
#                     "total_value": round(closing_price * item[1], 2)
#                 }
#                 total_value += stock_dict[item[2]]["total_value"]

#         for stock, value in stock_dict.items():
#             if stock != "portfolio_value":
#                 stock_dict[stock]["weighted_value"] = round((value["total_value"] / total_value) * 100, 2)

#         stock_dict["portfolio_value"] = round(total_value, 2)

#         return jsonify(stock_dict)
#     else:
#         print(f"No stocks found for user: {user}")
#         return jsonify({"message": "No stocks found for the user."})





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
#       
# if __name__ == '__main__':
#     # with app.app_context():
#     #     create_and_insert_user()
#     app.run(debug=True)




    