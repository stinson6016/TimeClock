from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import desc
from werkzeug.security import check_password_hash
from uuid import uuid4, UUID
from datetime import datetime, date

from . import db
from .models import Users, Punch
from .webforms import PunchForm

clock = Blueprint("clock", __name__)

@clock.route('/login/show')
def loginshow():
    form = PunchForm()
    form.name.choices = getUsers()
    form.process()
    return render_template('loginform.html',
                           form=form)

@clock.post('/login')
def login():
    form = PunchForm()
    user = form.name.data
    password = form.password.data
    
    if user == '':
        return '', 404

    check_user = Users.query.filter_by(id=user).first()
    if not check_password_hash(check_user.pass_hash, password):
        flash('Password Incorrect')
        form.name.choices = getUsers()
        form.name.default = user
        form.process()
        return render_template('loginform.html',
                               form=form)
    login_user(check_user)
    return redirect(url_for('clock.punches'))
  
@clock.route('/logout')
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('clock.loginshow'))

@clock.route('/punch')
@login_required
def onepunch():
    time_now = datetime.now()
    type = request.args.get('type', default='', type=str)
    edit_user = Users.query.get(current_user.id)
    print(type)
    if type == 'i' and current_user.last_clock: #punch in already punched in
        # flag current punch for review
        # add new punch and update user
        print("in -> in")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.flag = 'y'
        new_punch = Punch(id=uuid4(), clock_in=time_now,
                          user_id=current_user.id)
        db.session.add(new_punch)
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash('Clocked In')
        
    if type == 'i' and not current_user.last_clock: ### punch in not punched in
        # add new punch and update user
        print("out -> in")
        new_punch = Punch(id=uuid4(), clock_in=time_now,
                          user_id=current_user.id)
        db.session.add(new_punch)
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash('Clocked In')

    if type == 'o' and not current_user.last_clock: # punch out not punched in
        # add new punch out and clear user punch and flag for review
        print("out -> out")
        new_punch = Punch(id=uuid4(), clock_out=time_now,
                          flag='y', user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        flash('Clocked Out')

    if type == 'o' and current_user.last_clock: ### punch out and punched in
        # edit punch and clear user punch
        print("in -> out")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.clock_out = time_now
        edit_user.last_clock = None
        db.session.commit()
        flash('Clocked Out')
    
    return redirect(url_for('clock.punches'))

@clock.route('/punches')
@login_required
def punches():
    punches = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_in),desc(Punch.clock_out)).limit(20)
    return render_template('punches.html',
                           punches=punches)

@clock.route('/punch/flag')
@login_required
def punchflag():
    id = request.args.get('id', default='', type=UUID)
    flag = request.args.get('flag', default='flag', type=str)
    punch = Punch.query.get_or_404(id)
    punch.flag = 'n' if flag == 'unflag' else 'y'
    db.session.commit()
    return render_template('punch-row.html',
                           punch=punch)

def getUsers():
    users = Users.query.where(Users.active == 'y', Users.admin == 'n').order_by(Users.name)
    return_users = [("","")]
    for user in users:
        return_users.append((user.id, user.name))
    return return_users
