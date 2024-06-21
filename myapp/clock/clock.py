from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .login import login
from .profile import profile
from .punch import punch

from ..models import Users
from .webforms import PunchForm

clock = Blueprint("clock", __name__,
                  template_folder='templates', 
                  url_prefix='/clock')
clock.register_blueprint(login)
clock.register_blueprint(profile)
clock.register_blueprint(punch)

@clock.route('/')
def home():
    if current_user.is_authenticated and current_user.admin == 'y':
        flash('Please logout of Time Records to access the Time Clock')
        return redirect(url_for('records.main'), code=307)
    user_count = Users.query.count()
    if user_count == 0:
        return redirect(url_for('setup.show'), code=307)
    form = PunchForm()
    form.name.choices = [(''),('loading employees')]
    # form.name.default = 'loading'
    form.process()
    return render_template("clock.html",
                           form=form)

@clock.post('/showmain')
def showmain():
    if current_user.is_authenticated:
        return redirect(url_for('clock.punch.punches'), code=307)
    else:
        return redirect(url_for('clock.login.loginshow'), code=307)

@clock.post('/date')
def getdate():
    getdate = date.today()
    return render_template('clock-date.html',
                           getdate=getdate)

@clock.post('/showhelp')
@login_required
def showhelp():
    return render_template('help.html')

@clock.post('/hidehelp')
@login_required
def hidehelp():
    return render_template('help-min.html')