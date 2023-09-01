from flask import request
from . import api
from ..models import User, Cart, CartProduct, Product, db
from werkzeug.security import check_password_hash
import base64
from ..auth import token_auth_required, basic_auth_required, basic_auth, token_auth

@api.post('/signup')
def sign_up_API():
    try:
        data = request.json
        
        username = data['username']
        email = data['email']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user:
            return {
            'status': 'not ok',
            'message': 'That username is already taken.'
        }, 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            return {
            'status': 'not ok',
            'message': 'That email is already in use.'
        }, 400
        
        user = User(username,email,password)

        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username=username).first()
        cart = Cart(user.user_id)

        db.session.add(cart)
        db.session.commit()

        return {
            'status': 'ok',
            'message': 'Successfully created your user!'
        }, 201
    except:
        return {
            'status': 'not ok',
            'message': "Something went wrong, please try again."
        }, 400
    
@api.post('/login')
@basic_auth_required
def login_API(user):
    return {
        'status': 'ok',
        'user': user.to_dict(),
        'message': 'Successfully logged in!'
    }, 200

@api.get('/products')
def get_all_products_API():
    products = Product.query.all()
    return {
        'status': 'ok',
        'results': len(products),
        'products': [p.to_dict() for p in products]
    }, 200

@api.get('/product')
def get_single_product_API(product_id):
    product = Product.query.filter_by(product_id = product_id).first()
    return {
        'status': 'ok',
        'results': 1,
        'product': product.to_dict()
    }, 200

@api.post('/cart/add')
@token_auth_required
def add_to_cart_API(user):
    data = request.json
    product_id = data['product_id']
    product = Product.query.get(product_id)
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()

    if product:
        cart.total += product.price
        if cart_product:
            cart_product.quantity = cart_product.quantity + 1
            db.session.commit()
        else:
            new_cart_item = CartProduct(cart.cart_id,product_id,1)
            db.session.add(new_cart_item)
            db.session.commit()

        return {
            'status': 'ok',
            'message': 'Successfully added item to cart.'
        }, 200
    
    return {
        'status': 'not ok',
        'message': 'A product with that ID does not exist.'
    }, 404

@api.post('/cart/removeone')
@token_auth_required
def remove_one_from_cart_API(user):
    data = request.json
    product_id = data['product_id']
    product = Product.query.get(product_id)
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()
    
    if cart_product:
        if cart_product.quantity >= 2:
            cart_product.quantity = cart_product.quantity - 1
        else:
            db.session.remove(cart_product)
        cart.total -= product.price
        db.session.commit()
        return {
            'status': 'ok',
            'message': 'Successfully removed item from cart.'
        }, 200
    else:
        return {
            'status': 'not ok',
            'message': 'That product is not in the cart.'
        }, 404
    
@api.post('/cart/removeall')
@token_auth_required
def remove_all_from_cart_API(user):
    data = request.json
    product_id = data['product_id']
    product = Product.query.get(product_id)
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()
    total_reduction = product.price * cart_product.quantity
    
    if cart_product:
        cart.total -= total_reduction
        db.session.delete(cart_product)
        db.session.commit()
        return {
            'status': 'ok',
            'message': 'Successfully removed item(s) from cart.'
        }, 200
    else:
        return {
            'status': 'not ok',
            'message': 'That product is not in the cart.'
        }, 404

@api.post('/cart/clear')
@token_auth_required
def clear_cart_API(user):
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    cart_products = CartProduct.query.filter_by(cart_id=cart.cart_id).all()

    if cart_products:
        cart.total -= cart.total
        for product in cart_products:
            db.session.delete(product)
        db.session.commit()
        return {
            'status': 'ok',
            'message': 'Successfully cleared cart.'
        }, 200
    else:
        return {
            'status': 'not ok',
            'message': 'Cannot clear the cart because it is already empty.'
        }, 404

@api.get('/cart')
@token_auth_required
def get_cart_API(user):
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id).all()
    cart_products = []
    if cart_product:
        for cp in cart_product:
            product = Product.query.filter_by(product_id=cp.product_id).first()
            dict_product = product.to_dict()
            dict_product['quantity'] = cp.quantity
            cart_products.append(dict_product)
    return {
        'status': 'ok',
        'results': len(cart_products),
        'cart': cart_products
    }, 200