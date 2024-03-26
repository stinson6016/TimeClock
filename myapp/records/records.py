from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from .entries import entries
from .users import users
from .company import company
from .hours import hours

from .webforms import RecordsLogin, UserPW
from .. import db
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
            flash("Please log out of Time Clock to access the Time Records")
            return redirect(url_for('clock.home'))
    user_count = Users.query.count()
    if user_count == 0:
        return redirect(url_for('setup.show'))
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
    pw_form=UserPW()
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
    
    if check_user.pw_change == 'y':
        message = 'Must reset password to login'
        return render_template('recordslogin-pw.html',
                               form=pw_form,
                               editid=check_user.id,
                               message=message)


    login_user(check_user)
    return redirect(url_for('records.mainportal'))

@records.post('/login/pwreset')
def loginpwreset():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    if not check_password_hash(user.pass_hash, form.admin_pass.data):
        message = 'current password incorrect'
        return render_template('recordslogin-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    if form.password1.data != form.password2.data:
        message = 'passwords do not match'
        return render_template('recordslogin-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    user.pass_hash = generate_password_hash(form.password1.data)
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    login_user(user)
    return redirect(url_for('records.mainportal'))

@records.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('records.loginshow'))

