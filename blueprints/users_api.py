from flask import Blueprint, render_template, redirect
from flask_login import LoginManager, logout_user, login_required, current_user, login_user

from data import db_session
from data.users import User
from forms.users import EditForm, LoginForm, RegisterForm

users = Blueprint('users', __name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditForm(obj=current_user)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not user.check_password(form.password.data):
            return render_template('users/edit.html', title='Profile',
                                   form=form,
                                   message="Wrong password")
        if form.new_password.data != form.new_password_again.data:
            return render_template('users/edit.html', title='Profile',
                                   form=form,
                                   message="Passwords don't match")
        if db_sess.query(User).filter(User.email == form.email.data).first() and form.email.data != user.email:
            return render_template('users/edit.html', title='Profile',
                                   form=form,
                                   message="User with this email already exists")
        user.name = form.name.data
        user.email = form.email.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data
        if len(form.new_password.data) > 0:
            user.set_password(form.new_password.data)
        db_sess.commit()
        return render_template('users/edit.html', title='Profile', form=form, message="Profile was updated")
    return render_template('users/edit.html', title='Profile', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('users/login.html',
                               message="Wrong email or password",
                               form=form)
    return render_template('users/login.html', title='Authorization', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('users/register.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('users/register.html', title='Registration',
                                   form=form,
                                   message="This user already exists")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('users/register.html', title='Registration', form=form)


@users.route('/users_list/<int:user_id>')
@login_required
def edit_user(user_id):
    db_sess = db_session.create_session()
    if current_user.is_admin:
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user.is_admin:
            user.is_admin = False
        else:
            user.is_admin = True
        db_sess.commit()
        return redirect('/users_list')


@users.route('/users_list')
@login_required
def show_users():
    db_sess = db_session.create_session()
    all_users = db_sess.query(User).all()
    return render_template('users/users_list.html', users=all_users)


@users.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.is_admin or user_id == current_user.id:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        db_sess.delete(user)
        db_sess.commit()
    return redirect('/')
