from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from .entries import entries
from .users import users
from .company import company
from .hours import hours

from .webforms import RecordsLogin
from ..extra import getUsersAdmins
from ..models import Users

records = Blueprint("records", __name__,
                    template_folder='templates')
records.register_blueprint(entries, url_prefix='/entries')
records.register_blueprint(users, url_prefix='/users')
records.register_blueprint(company, url_prefix='/company')
records.register_blueprint(hours, url_prefix='/hours')

@records.route('/')
def main():
    if current_user.is_authenticated:
        if current_user.admin != 'y':
            return redirect(url_for('clock.home'))
    return render_template("records.html")

@records.route('/showmain')
def showmain():
    if current_user.is_authenticated:
        return redirect(url_for('records.mainportal'))
    else: 
        return redirect(url_for('records.loginshow'))
        
@records.route('/portal')
@login_required
def mainportal():
    return render_template('portal.html')

@records.route('/login/show')
def loginshow():
    form = RecordsLogin()
    form.name.choices = getUsersAdmins()
    form.process()
    return render_template('recordslogin.html',
                           form=form)

@records.post('/login')
def login():
    form = RecordsLogin()
    user = form.name.data
    password = form.password.data
    if user == '':
        return '', 404
    check_user = Users.query.filter_by(id=user).first_or_404()
    if not check_password_hash(check_user.pass_hash, password):
        flash('Password Incorrect')
        form.name.choices = getUsersAdmins()
        form.name.default = user
        form.process()
        return render_template('recordslogin.html',
                               form=form)
    login_user(check_user)
    return redirect(url_for('records.mainportal'))


@records.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('records.loginshow'))

