from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from ..models import Device, User
from . import site
from .. import login_manager


@site.route('/', methods=['GET'])
@site.route('/index', methods=['GET'])
def index():
    return render_template('index.html', devices=Device.query.all(), user=current_user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@site.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = str(request.form['username'])
            password = str(request.form['password'])
            remember_me = False
            if 'remember_me' in request.form:
                remember_me = True
            user = User.get_by_username(username)
            if user is not None and user.check_password(password):
                login_user(user, remember_me)
                print(str(user) + ' logged in!')
                return redirect(request.args.get('next') or url_for('site.index'))
            flash("Login failed!")
    return render_template('login.html')


@site.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('site.index'))


@site.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        family_name = request.form['family_name']
        holder = request.form['user_id']
        owner = request.form['owner']
        serial_number = request.form['serial_number']
        article_number = request.form['article_number']
        Device.add_device(name, family_name, holder, owner, serial_number, article_number)
        flash('Device added: ' + name)
        return redirect(url_for('index'))
    return render_template('add.html')


@site.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@site.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
