from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
# app.config['JWT_HEADER_TYPE'] = 'Token'  # change Bearer prefix
app.secret_key = 'pyziko'
# app.config['JWT_SECRET_KEY']      # The secret key used to encode and decode JWTs if not set, app.secret_key is used

api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  # not creating /auth


# identity here is what we passed as identity in UserLogin ->> user line 59
# This is where we pass in all our Authorities (role and permissions) of a user to the user token
# sample below, verify in jwt.io
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # don't hard code read from database or config file
        return {'is_admin': True}
    return {"is_admin": False}


# when the token has expired we can send back custom messages as below, overriding the default message
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        "description": " The token has expired",
        "error": "token expired"
    }), 401


# called when the token sent is not a valid jwt, overrides the default
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': "Signature verification failed",
        "error": "invalid token"
    }), 401


# called when no jwt is sent at all, when jwt is required, so we can override the default
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': "Request does not contain an access token",
        "error": "authorization_required"
    }), 401


# called when an endpoint like (Item :: POST), which requires a fresh token, gets a non-fresh token
@jwt.needs_fresh_token_loader
def missing_token_callback(error):
    return jsonify({
        'description': "The token is not fresh",
        "error": "fresh_token_required"
    }), 401


# say user clicks log out, we add the user's token to the revoked list and then call this fn saying user is logged out,
# log in again
@jwt.revoked_token_loader
def missing_token_callback(error):
    return jsonify({
        'description': "The Token has been revoked",
        "error": "token revoked"
    }), 401


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db

    db.init_app(app)
    app.run(port=5000, debug=True)
