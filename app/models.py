from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from secrets import token_hex

db = SQLAlchemy()

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(45),nullable=False,unique=True)
    email = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String,nullable=False)
    admin = db.Column(db.Boolean,nullable=False,default=False)
    date_created = db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    token = db.Column(db.String,nullable=False,unique=True)

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.token = token_hex(16)
    
    def get_id(self):
        try:
            return str(self.user_id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'token': self.token,
            'admin': self.admin
        }

class Cart(db.Model):
    cart_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id', ondelete="CASCADE"),nullable=False,unique=True)
    total = db.Column(db.Float,nullable=False,default=0.00)

    def __init__(self,user_id):
        self.user_id = user_id

class CartProduct(db.Model):
    cart_product_id = db.Column(db.Integer,primary_key=True)
    cart_id = db.Column(db.Integer,db.ForeignKey('cart.cart_id', ondelete="CASCADE"),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('product.product_id', ondelete="CASCADE"),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)

    def __init__(self, cart_id, product_id, quantity):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

class Product(db.Model):
    product_id = db.Column(db.Integer,primary_key=True)
    sku = db.Column(db.Integer,nullable=False,unique=True)
    product_name = db.Column(db.String(25),nullable=False,unique=True)
    img_url = db.Column(db.String,nullable=False)
    description = db.Column(db.String,default='')
    price = db.Column(db.Float,nullable=False,default=0.00)

    def __init__(self,sku,product_name,img_url,description,price):
        self.sku = sku
        self.product_name = product_name
        self.img_url = img_url
        self.description = description
        self.price = price
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'sku': self.sku,
            'product_name': self.product_name,
            'img_url': self.img_url,
            'description': self.description,
            'price': self.price
        }