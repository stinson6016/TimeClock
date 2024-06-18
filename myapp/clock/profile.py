from datetime import datetime, datetime
from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db
from ..models import Users
from .webforms import UserProfile, UserPW

profile = Blueprint("profile", __name__,
                  template_folder='templates', 
                  url_prefix='/profile')


@profile.post('/show')
@login_required
def profileshow():
    return render_template('profile/profile.html')

@profile.post('/editshow')
@login_required
def profileeditshow():
    form = UserProfile()
    form.name.default = current_user.name
    form.email.default = current_user.email
    form.time_format.default = current_user.time_format
    form.last_punch.default = current_user.last_punch
    form.process()
    return render_template('profile/profile-edit.html',
                           form=form)

@profile.post('/edit')
@login_required
def profileedit():
    user = Users.query.get(current_user.id)
    form = UserProfile()
    check_email = Users.query.where(Users.email == form.email.data, Users.id != user.id, Users.admin=='n').first()
    if check_email and form.email.data:
        flash("that email already in use")
        return render_template('profile/profile-edit.html',
                           form=form)
    user.name = form.name.data
    user.email = form.email.data
    user.time_format = form.time_format.data
    user.last_punch = form.last_punch.data
    db.session.commit()
    return render_template('profile/profile.html')

@profile.post('/pwshow')
@login_required
def profilepwshow():
    form = UserPW()
    return render_template('profile/profile-pw.html',
                           form=form)

@profile.post('/pwedit')
@login_required
def profilepwedit():
    user = Users.query.get(current_user.id)
    form = UserPW()
    if not check_password_hash(current_user.pass_hash, form.admin_pass.data):
        message = "current password incorrect"
        return render_template('profile/profile-pw.html',
                               form=form,
                               message=message)
    
    if form.password1.data != form.password2.data:
        message = "passwords do not match"
        return render_template('profile/profile-pw.html',
                               form=form,
                               message=message)
    
    pass_hash = generate_password_hash(form.password1.data)
    user.pass_hash = pass_hash
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    return render_template('profile/profile.html')