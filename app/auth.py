from flask import request
from .models import User
import base64
from werkzeug.security import check_password_hash
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            return user
        
@token_auth.verify_token
def verify_token(token):
    user = User.query.filter_by(token = token).first()
    if user:
        return user

def basic_auth_required(func):
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            val = request.headers['Authorization']
            encoded_version = val.split()[1]
            x = base64.b64decode(encoded_version.encode('ascii')).decode('ascii')
            username, password = x.split(':')
        else:
            return {
                'status': 'not ok',
                'message': 'Please Add Authorization Header with Basic Auth Format.'
            }, 401
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return {
            'status': 'not ok',
            'message': 'There is no user with that username'
        }, 401
        
        if check_password_hash(user.password, password):
            return func(user=user, *args, **kwargs)
        return {
            'status': 'not ok',
            'message': 'Incorrect username/password'
        }, 401
    
    decorated.__name__ = func.__name__        
    return decorated

def token_auth_required(func):

    def decorated(*args, **kwargs):
        
        if 'Authorization' in request.headers:
            val = request.headers['Authorization']
            type, token = val.split()
            if type == 'Bearer':
                token = token
            else:
                return {
                'status': 'not ok',
                'message': 'Please Add Authorization Header with Bearer Token Format.'
            }, 401

            user = User.query.filter_by(token=token).first()
            if user:
                return func(user=user, *args, **kwargs)
            else:
                return {
                    'status': 'not ok',
                    'message': 'Invalid Token'
                }, 401
        else:
            return {
                'status': 'not ok',
                'message': 'Please add Authorization Header with Bearer Token Format.'
            }, 401
    decorated.__name__ = func.__name__        
    return decorated