from datetime import datetime, datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from .. import db
from ..extra import get_users
from ..models import Users
from .webforms import PunchForm, UserPW

login = Blueprint("login", __name__,
                  template_folder='templates',
                  url_prefix='/login')


@login.post('/show')
def loginshow():
    form = PunchForm()
    form.name.choices = get_users()
    form.process()
    return render_template('login/login.html',
                           form=form)

@login.post('/main')
def loginmain():
    form = PunchForm()
    pw_form = UserPW()
    user = form.name.data
    password = form.password.data
    
    if user == '':
        return '', 404

    check_user = Users.query.filter_by(id=user).first_or_404()
    if not check_password_hash(check_user.pass_hash, password):
        logging.warning(f'password incorrect {check_user.name}')
        flash('Password Incorrect')
        form.name.choices = get_users()
        form.name.default = user
        form.process()
        return render_template('login/login.html',
                               form=form)
    
    if check_user.pw_change == 'y':
        logging.warning(f'must rest password {check_user.name}')
        message='Must reset password to login'
        return render_template('login/pw.html',
                               form=pw_form,
                               editid=check_user.id,
                               message=message)
    
    login_user(check_user)
    logging.info(f'Employee - {current_user.name} logged in')
    return redirect(url_for('clock.punch.punches'), code=307)

@login.post('/pwreset')
def loginpwreset():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    if not check_password_hash(user.pass_hash, form.admin_pass.data):
        logging.warning(f'password reset incorrect password {user.name}')
        message = 'current password incorrect'
        return render_template('login/pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    if form.password1.data != form.password2.data:
        message='passwords do not match'
        return render_template('login/pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    user.pass_hash = generate_password_hash(form.password1.data)
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    login_user(user)
    return redirect(url_for('clock.punch.punches'), code=307)

@login.post('/logout')
def logout():
    logging.info(f'Employee - {current_user.name} logged out')
    logout_user()
    flash('logged out')
    return redirect(url_for('clock.login.loginshow'), code=307)
