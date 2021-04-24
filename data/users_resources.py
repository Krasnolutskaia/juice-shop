from flask import jsonify
from flask_restful import abort, Resource, reqparse
from werkzeug.security import generate_password_hash

from data import db_session
from data.products import Product
from data.users import User

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('address')
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)
parser.add_argument('phone_number')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    product = session.query(Product).get(user_id)
    if not product:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        product = session.query(Product).get(user_id)
        return jsonify({'user': product.to_dict(
            only=('name', 'email', 'phone_number', 'address'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(Product).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'email', 'phone_number', 'address')) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            email=args['email'],
            phone_number=args['phone_number'],
            address=args['address'],
            id_admin=args['is_admin'],
            hashed_password=generate_password_hash(args['password'])
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
