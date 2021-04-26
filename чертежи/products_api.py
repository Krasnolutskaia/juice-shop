from flask import Blueprint, abort, render_template, redirect, url_for, request
from flask_login import current_user

from data import db_session
from forms.products import ProductForm
from data.products import Product

products = Blueprint('products', __name__)


@products.route('/')
def index():
    db_sess = db_session.create_session()
    q = request.args.get('q', '')
    if q:
        all_products = db_sess.query(Product).filter(
            (Product.name.like(f'%{q.lower()}%')) | (Product.name.like(f'%{q.upper()}%')) | (
                Product.name.like(f'%{q.capitalize()}%'))).all()
        if len(all_products) == 0:
            all_products = db_sess.query(Product).filter(
                (Product.description.like(f'%{q.lower()}%')) | (Product.description.like(f'%{q.upper()}%')) | (
                    Product.description.like(f'%{q.capitalize()}%'))).all()
            if len(all_products) == 0:
                all_products = 'Nothing was found'
        else:
            res = db_sess.query(Product).filter(
                (Product.description.like(f'%{q.lower()}%')) | (Product.description.like(f'%{q.upper()}%')) | (
                    Product.description.like(f'%{q.capitalize()}%'))).all()
            for prod in res:
                if prod in all_products:
                    res.remove(prod)
            if len(res) != 0:
                all_products += res
    else:
        all_products = db_sess.query(Product).all()
    sort_by = request.args.get('sort_by', '')
    if sort_by:
        if sort_by == 'Rank by highest price':
            all_products = sorted(all_products, key=lambda x: -x.price_cents)
        elif sort_by == 'Rank by lowest price':
            all_products = sorted(all_products, key=lambda x: x.price_cents)
    return render_template('products/show.html', products=all_products)


@products.route('/products_list')
def products_list():
    db_sess = db_session.create_session()
    all_products = db_sess.query(Product).all()
    return render_template('products/products.html', products=all_products)


@products.route('/<int:product_id>')
def details(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == product_id).first()
    return render_template('products/details.html', product=product)


@products.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.is_admin:
        form = ProductForm()
        if form.validate_on_submit():
            product = Product() 
            product.name = form.name.data
            product.description = form.description.data
            product.price_cents = int(form.price.data * 100) 
            product.picture_url = form.picture_url.data
            db_sess = db_session.create_session()
            db_sess.add(product)
            db_sess.commit()
            return redirect(url_for('.details', product_id=product.id))
        return render_template('products/new.html', form=form)
    return redirect('/')


@products.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        form = ProductForm(obj=product, price=product.price_cents / 100)
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price_cents = int(form.price.data * 100)
            product.picture_url = form.picture_url.data
            db_sess.commit()
            return redirect(url_for('.details', product_id=product.id))
        return render_template('products/edit.html', product=product, form=form)
    return redirect('/')


@products.route('/product_delete/<int:product_id>', methods=['GET', 'POST'])
def delete(product_id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        if not product:
            abort(404)
        product_name = product.name
        db_sess.delete(product)
        db_sess.commit()
        return render_template('products/deleted.html', product_name=product_name)
    return redirect('/')
