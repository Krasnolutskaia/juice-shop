from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required

from data import db_session
from data.products import Product
from data.users import User

basket = Blueprint('basket', __name__)


@basket.route('/add_to_basket/<int:product_id>')
@login_required
def add_to_basket(product_id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).filter(Product.id == product_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.products.append(prod)
    db_sess.commit()
    return redirect('/')


@basket.route('/view_basket')
@login_required
def view_basket():
    total_price = sum([prod.price_cents for prod in current_user.products]) / 100
    return render_template('basket.html', products=current_user.products, total_price=total_price)


@basket.route('/delete_from_basket/<int:product_id>')
@login_required
def delete_from_basket(product_id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).filter(Product.id == product_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.products.remove(prod)
    db_sess.commit()
    return redirect('/view_basket')
