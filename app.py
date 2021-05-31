from flask import Flask
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
