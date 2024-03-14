from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence
from sqlalchemy.schema import Identity
from sqlalchemy.orm import relationship

db = SQLAlchemy()
#i used chat.gpt to implement the right logic and asjust it to my code 
class Users(db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # Added email field
    stocks = db.relationship('Stock', backref='owner', lazy='dynamic')

    def dict(self):
        return {
            'id': self.id,
            'password': self.password_hash,
            'user_name': self.user_name,
            'user_mail': self.email
        }
    
    
class Stocks(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ticker': self.ticker,
            'quantity': self.quantity,
        }