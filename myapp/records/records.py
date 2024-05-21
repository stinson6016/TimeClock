from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from os import getenv
import logging

from .company import company
from .entries import entries
from .hours import hours
from .users import users

from .webforms import RecordsLogin, UserPW, LostPassword, PasswordSet
from .. import db
from ..extra import get_users_admins
from ..models import Users
from ..extensions import mail

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
    form = RecordsLogin()
    form.name.choices = [(''), ('loading admins...')]
    form.process()
    email_active:str = getenv('EMAIL_ACTIVE')
    return render_template("records/records.html",
                           form=form,
                           email_active=email_active )

@records.post('/showmain')
def showmain():
    if current_user.is_authenticated:
        return redirect(url_for('records.mainportal'), code=307)
    else: 
        return redirect(url_for('records.loginshow'), code=307)
        
@records.post('/portal')
@login_required
def mainportal():
    return render_template('records/portal.html')

@records.post('/login/show')
def loginshow():
    form = RecordsLogin()
    form.name.choices = get_users_admins()
    form.process()
    email_active:str = getenv('EMAIL_ACTIVE')
    return render_template('records/recordslogin.html',
                           form=form,
                           email_active=email_active)

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
        logging.warning(f'incorrect password {check_user.name}')
        flash('Password Incorrect')
        form.name.choices = get_users_admins()
        form.name.default = user
        form.process()
        return render_template('records/recordslogin.html',
                               form=form)
    
    if check_user.pw_change == 'y':
        logging.warning(f'must change password {check_user.name}')
        message = 'Must reset password to login'
        return render_template('records/recordslogin-pw.html',
                               form=pw_form,
                               editid=check_user.id,
                               message=message)


    login_user(check_user)
    logging.info(f'ADMIN - {current_user.name} logged in')
    return redirect(url_for('records.mainportal'), code=307)

@records.post('/login/pwreset')
def loginpwreset():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    if not check_password_hash(user.pass_hash, form.admin_pass.data):
        logging.warning(f'password change incorrect password {user.name}')
        message = 'current password incorrect'
        return render_template('records/recordslogin-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    if form.password1.data != form.password2.data:
        message = 'passwords do not match'
        return render_template('records/recordslogin-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    user.pass_hash = generate_password_hash(form.password1.data)
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    login_user(user)
    return redirect(url_for('records.mainportal'), code=307)

@records.post('/logout')
def logout():
    logging.info(f'ADMIN - {current_user.name} logged in')
    logout_user()
    flash('Logged out')
    return redirect(url_for('records.loginshow'), code=307)

@records.post('/login/lostpw')
def loginlostpw():
    form = LostPassword()
    return render_template('records/records-lostpw.html',
                           form=form)

@records.post('/login/lostpw/send')
def loginlostpwsend():
    form = LostPassword()
    user = Users.query.where(Users.email==form.email.data).first()
    
    if user:
        pass_reset_url = make_token(user.id)
        msg = Message()
        msg.subject = "Password Reset Request"
        msg.recipients = [user.email]
        msg.html = render_template('records/email-pwreset.html',
                                    pass_reset_url=pass_reset_url)
        try:
            mail.send(msg)
        except:
            flash('email send failed, check server settings')
            return redirect(url_for('records.showmain'), code=307)
    flash('email sent, check your spam folder')
    return redirect(url_for('records.showmain'), code=307)

@records.get('/resetpassword')
def resetpw():
    form = PasswordSet()
    token = request.args.get('token')
    id = validate_token(token)
    if id == False:
        flash('Link error, link might be expired')
        return redirect(url_for('records.main'), code=307)
    return render_template('records/records-pw-link.html',
                           form=form,
                           id=id)

@records.post('/resetpassword/update')
def resetpwupdate():
    form = PasswordSet()
    if form.password1.data != form.password2.data:
        flash('passwords do not match')
        return render_template('records/records-pw-link.html',
                               form=form)
    id = request.args.get('id', default='', type=int)
    user = Users.query.get_or_404(id)
    user.pass_hash = generate_password_hash(form.password1.data)
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    flash('password reset')
    return redirect(url_for('records.main'), code=307)

def make_token(userid:int) -> str:
    from os import getenv
    password_reset_serializer = Serializer(getenv('SECRET_KEY'))

    password_reset_url:str = url_for(
        'records.resetpw',
        token=password_reset_serializer.dumps(userid, salt=getenv('PASSWORD_RESET_SALT')),
        _external=True)
    return password_reset_url

def validate_token(token, expire_time=600) -> int:
    """from token and expire_time to confirm user's email"""
    from os import getenv
    serializercheck = Serializer(getenv('SECRET_KEY'))
    try:
        userid = serializercheck.loads(token, max_age=expire_time, salt=getenv('PASSWORD_RESET_SALT'))
    except Exception:
        return False
    return userid 