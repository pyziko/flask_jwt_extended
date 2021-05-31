from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price", type=float, required=True, help="This field cannot be left blank")
    parser.add_argument("store_id", type=int, required=True, help="Every item needs a store id")

    @jwt_required()   # flask_jwt_extended >4.0.0  parenthesis, and Bearer is used in request not JWT
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found"}, 404

    # This ensures that a new item can be created wen u just logged in- fresh_toke_required
    # NOTE the parameter fresh, not refresh
    # Usage: to ensure a critical action requires user logging in or entering their password
    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"An item with name '{name}' already exist"}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)  # **data => data["price"], data["store_id"]
        try:
            item.save_to_db()
        except:
            return {"message": "An Error occurred inserting the item"}, 500  # Internal Server Error

        return item.json(), 201

    # sample on how to use claims, we can extract claims as blow
    @jwt_required()
    def delete(self, name: str):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin Privilege required"}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": "Item deleted"}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    # can be used to return some  data if user is logged in and another data if not logged in
    # optional=True means is not compulsory if user is logged in
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items": items}, 200
        return {
            "items": [item["name"] for item in items],
            "message": "More data available if you login."
        }, 200
