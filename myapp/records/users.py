from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

from .webforms import UserEdit, UserNew, UserPW
from .. import db 
from ..models import Users, Punch

users = Blueprint('users', __name__,
                  template_folder='templates')

@users.post('/show')
@login_required
def show():
    return render_template('users/users.html',
                           disabled='n',
                           page='u')

@users.post('/showall')
@login_required
def showall():
    disabled = request.args.get('disabled', default='n', type=str)
    if disabled == 'y':
        users = Users.query.order_by(desc(Users.admin), Users.name)
    else:
        users = Users.query.where(Users.active!='n').order_by(desc(Users.admin), Users.name)
    return render_template('users/users-table.html', 
                           users=users,
                           disabled=disabled,
                           page='u')

@users.post('/newshow')
@login_required
def newshow():
    form = UserNew()
    return render_template('users/users-new.html',
                           form=form)

@users.post('/new')
@login_required
def new():
    form = UserNew()
    
    check_email = Users.query.where(Users.email == form.email.data, Users.admin == form.admin.data).first()
    if check_email and form.email.data:
        message:str  = "email address in use"
        return render_template('/users/users-new.html',
                               form=form,
                               message=message)
    if form.password1.data != form.password2.data:
        message2:str  = "passwords do not match"
        return render_template('/users/users-new.html',
                               form=form,
                               message2=message2)
    password = generate_password_hash(form.password1.data)
    new_user = Users(name=form.name.data, email=form.email.data,
                     pass_hash=password, active=form.active.data,
                     pw_change=form.change.data, pw_last=datetime.now(),
                     admin=form.admin.data)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('records.users.showrow', 
                            id=new_user.id), code=307)

@users.post('/cancel')
@login_required
def cancel():
    return '', 200

@users.post('/editshow')
@login_required
def editshow():
    id = request.args.get('id', default='', type=int)
    user = Users.query.get_or_404(id)
    form = UserEdit()
    form.name.default = user.name
    form.email.default = user.email
    form.active.default = user.active
    form.change.default = user.pw_change
    form.admin.default = user.admin
    form.process()
    return render_template('users/users-edit.html',
                           form=form,
                           user=user)

@users.post('/edit')
@login_required
def edit():
    id = request.args.get('id', default = '', type=int)
    user = Users.query.get_or_404(id)
    form = UserEdit()
    check_email = Users.query.where(Users.email == form.email.data, Users.admin==form.admin.data).first()
    if check_email and user.email != form.email.data and form.email.data:
        message:str  = "email address in use"
        return render_template('/users/users-edit.html',
                               form=form,
                               user=user,
                               message=message)
    user.name = form.name.data
    user.email = form.email.data
    if user.id != current_user.id:
        user.active = form.active.data
        user.pw_change = form.change.data
        user.admin = form.admin.data
    db.session.commit()
    return redirect(url_for('records.users.showrow',
                            id=user.id), code=307)

@users.post('/showrow')
@login_required
def showrow():
    id = request.args.get('id', default = '', type =int)
    user = Users.query.get_or_404(id)
    return render_template('users/users-row.html',
                           user=user)

@users.delete('/delete')
@login_required
def delete():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    check_punch = Punch.query.where(Punch.user_id==user.id).count()
    if check_punch > 0:
        return '', 404
    db.session.delete(user)
    db.session.commit()
    return '', 200

@users.post('/passwordshow')
@login_required
def passwordshow():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    return render_template('users/users-password.html',
                           form=form,
                           user=user)

@users.post('/password')
@login_required
def password():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    if not check_password_hash(current_user.pass_hash, form.admin_pass.data):
        message:str = 'Admin password incorrect'
        return render_template('users/users-password.html',
                               form=form,
                               user=user,
                               message=message)
    if not form.password1.data == form.password2.data:
        message:str = 'passwords do not match'
        return render_template('users/users-password.html',
                               form=form,
                               user=user,
                               message=message)
    pass_hash = generate_password_hash(form.password1.data)
    user.pass_hash = pass_hash
    user.pw_last = datetime.now()
    user.pw_change = 'n'
    db.session.commit()
    return redirect(url_for('records.users.showrow',
                            id=user.id), code=307)

@users.post('/showkey')
@login_required
def showkey():
    return render_template('users/users-key.html')

@users.post('/hidekey')
@login_required
def hidekey():
    return render_template('users/users-key-min.html')