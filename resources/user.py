import hmac

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource, reqparse

from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username", type=str, required=True, help="This field cannot be left blank")
_user_parser.add_argument("password", type=str, required=True, help="This field cannot be left blank")


class UserRegister(Resource):  # todo INFO: remember to add it as a resource

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "User with username '{}' already exists".format(data["username"])}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully"}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)

        return user.json() if user else {"message": "user not found"}, 404

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": "user not found"}, 404
        user.delete_from_db()
        return {"message": "User deleted"}, 200


# using flask_jwt rather than flask_jwt_extended
class UserLogin(Resource):

    @classmethod
    def post(cls):
        # get data from parse
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data['username'])

        # check password --> this is what the 'authenticate' function used to do
        if user and hmac.compare_digest(user.password, data['password']):
            # identity= is what the identity function used to do
            # we can use username, i.e identity=username here rather than user_id
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {"message": "Invalid credentials"}, 401
