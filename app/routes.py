from flask import render_template, request, redirect, url_for, flash
from app import app
from .forms import LoginForm, SignUpForm, AddProductForm
from .models import User, db, Cart, Product, CartProduct
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import pip._vendor.requests as r

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signUpPage():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            if username_in_db(username):
                flash('The username already exists. Please enter another username.', 'danger')
                return redirect(url_for('signUpPage'))

            elif email_in_db(email):
                flash('The email is already in use. Please enter another email.', 'danger')
                return redirect(url_for('signUpPage'))
            
            else:
                # add user to database
                user = User(username,email,password)

                db.session.add(user)
                db.session.commit()

                user = User.query.filter_by(username=username).first()
                user_id = user.user_id
                cart = Cart(user_id)

                db.session.add(cart)
                db.session.commit()

                flash('Successfully created an account.', 'success')

                return redirect(url_for('loginPage'))

        else:
            flash('Passwords do not match. Please try again.', 'danger')
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET','POST'])
def loginPage():
    form = LoginForm()
    message = None
    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            password = form.password.data
            
            # check if user is in database
            user = User.query.filter_by(username=username).first()

            if user:
                if check_password_hash(user.password, password):
                    login_user(user)
                    flash('Successfuly logged in.', 'success')
                    return redirect(url_for('homePage'))
                else:
                    flash('Incorrect password.', 'danger')
            else:
                flash('The username does not exist.', 'danger')
        else:
            flash('An error has ocurred. PLease submit a valid form.', 'danger')

    return render_template('login.html', form=form, message=message)

def username_in_db(username):
    return User.query.filter_by(username=username).first()

def email_in_db(email):
    return User.query.filter_by(email=email).first()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('loginPage'))

@app.route('/addproduct', methods = ["GET", "POST"])
@login_required
def addProduct():
    form = AddProductForm()
    if request.method == "POST":
        if form.validate():
            sku = form.sku.data
            product_name = form.product_name.data
            img_url = form.img_url.data
            description = form.description.data
            price = form.price.data

            new_product = Product(sku, product_name, img_url, description, price)

            db.session.add(new_product)
            db.session.commit()
            flash('Succesfully added new product!', 'success')
            return redirect(url_for('homePage'))

    return render_template('addproduct.html', form = form)

@app.route('/products', methods = ["GET", "POST"])
def products():
    products = Product.query.all()
    return render_template('products.html', products = products)

@app.route('/addtocart/<product_id>', methods = ["GET", "POST"])
@login_required
def addToCart(product_id):
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart:
        flash('You need to log in before you can add items to your cart.', 'warning')
        return redirect(url_for('loginPage'))
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()
    cart_product_price = Product.query.filter_by(product_id = product_id).first().price
    if cart_product:
        cart_product.quantity = cart_product.quantity + 1
        cart.total += cart_product_price
        db.session.commit()
        flash('Succesfully added an additional unit of the product to the cart!', 'success')
        return redirect(url_for('products'))
    else:
        new_cart_item = CartProduct(cart.cart_id,product_id,1)
        cart.total += cart_product_price
        db.session.add(new_cart_item)
        db.session.commit()
        flash('Succesfully added the product to the cart!', 'success')
        return redirect(url_for('products'))
    
@app.route('/cart', methods = ["GET", "POST"])
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    products = dict()
    # if not cart:
    #     flash('You need to log in before you can view your cart.', 'warning')
    #     return redirect(url_for('loginPage'))
    # else:
    cart_products = CartProduct.query.filter_by(cart_id=cart.cart_id).all()
    for cp in cart_products:
        products[cp.product_id] = [Product.query.filter_by(product_id=cp.product_id).first(),cp.quantity]

    return render_template('cart.html',products=products,total=cart.total)

@app.route('/removeallunitsfromcart/<product_id>', methods = ["GET", "POST"])
@login_required
def removeAllUnitsFromCart(product_id):
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart:
        flash('You need to log in before you can add items to your cart.', 'warning')
        return redirect(url_for('loginPage'))
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()
    cart_product_price = Product.query.filter_by(product_id = product_id).first().price
    total_reduction = cart_product_price * cart_product.quantity
    if cart_product:
        cart.total -= total_reduction
        db.session.delete(cart_product)
        db.session.commit()
        flash('Succesfully removed all units of the product from the cart!', 'success')
        return redirect(url_for('cart'))
    else:
        flash('At least 1 item must be in the cart before removing items from the cart.', 'warning')
        return redirect(url_for('cart'))

@app.route('/removeonefromcart/<product_id>', methods = ["GET", "POST"])
@login_required
def removeOneFromCart(product_id):
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart:
        flash('You need to log in before you can add items to your cart.', 'warning')
        return redirect(url_for('loginPage'))
    cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id,product_id=product_id).first()
    total_reduction = Product.query.filter_by(product_id = product_id).first().price
    if cart_product:
        if cart_product.quantity >= 2:
            cart_product.quantity = cart_product.quantity - 1
            cart.total -= total_reduction
            flash('Succesfully removed a unit of the product from the cart!', 'success')
        else:
            removeAllUnitsFromCart(product_id)
        db.session.commit()
        return redirect(url_for('cart'))
    else:
        flash('At least 1 item must be in the cart before removing items from the cart.', 'warning')
        return redirect(url_for('cart'))
    
@app.route('/clearcart', methods = ["GET", "POST"])
@login_required
def clearCart():
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()
    if not cart:
        flash('You need to log in before you can clear your cart.', 'warning')
        return redirect(url_for('loginPage'))
    cart_products = CartProduct.query.filter_by(cart_id=cart.cart_id).all()
    for product in cart_products:
        db.session.delete(product)
    cart.total -= cart.total
    db.session.commit()
    
    flash('Successfully cleared the cart.', 'success')
    return redirect(url_for('cart'))