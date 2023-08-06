from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class SignUpForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Your Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField()

class AddProductForm(FlaskForm):
    sku = StringField(label='SKU', validators=[DataRequired()])
    product_name = StringField(label='Product Name', validators=[DataRequired()])
    img_url = StringField(label='Img URL', validators=[DataRequired()])
    description = StringField(label='Description', validators=[DataRequired()])
    price = StringField(label='Price', validators=[DataRequired()])
    submit = SubmitField()