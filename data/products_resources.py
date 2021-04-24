from flask import jsonify
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.products import Product


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('description')
parser.add_argument('price', required=True)
parser.add_argument('picture')


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        return jsonify({'product': product.to_dict(
            only=('name', 'description', 'price_cents', 'picture_url'))})

    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify({'products': [item.to_dict(
            only=('name', 'description', 'price_cents', 'picture_url')) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            name=args['name'],
            description=args['description'],
            price=args['price'],
            picture_url=args['picture']
        )
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
