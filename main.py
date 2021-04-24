from flask import Flask, render_template
from flask_restful import Api
from flask_login import current_user
import os

from blueprints.users_api import login_manager, users
from data import db_session, products_resources, users_resources
from blueprints.products_api import products
from blueprints.basket_api import basket
from data.products import Product

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager.init_app(app)
api = Api(app)
api.add_resource(products_resources.ProductListResource, '/api/products')
api.add_resource(products_resources.ProductResource, '/api/products/<int:product_id>')
api.add_resource(users_resources.UserListResource, '/api/users')
api.add_resource(users_resources.UserResource, '/api/users/<int:user_id>')


@app.route('/buy/<int:product_id>')
def buy(product_id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).filter(Product.id == product_id).first()
    return render_template('buy.html', products=[prod], total_price=prod.price_cents / 100, count=1)


@app.route('/buy')
def buy_all():
    total_price = sum([prod.price_cents / 100 for prod in current_user.products])
    count = len(current_user.products)
    return render_template('buy.html', products=current_user.products, total_price=total_price, count=count)


def main():
    port = int(os.environ.get("PORT", 5000))
    db_session.global_init("db/shop.sqlite")
    app.register_blueprint(products)
    app.register_blueprint(users)
    app.register_blueprint(basket)
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
