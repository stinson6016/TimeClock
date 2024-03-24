from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, time, datetime, date

from .. import db
from ..extra import getUsers, getTimeTotal
from ..models import Users, Punch
from .webforms import PunchForm, UserProfile, UserPW

clock = Blueprint("clock", __name__,
                  template_folder='templates')

@clock.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.admin == 'y':
            flash('Please logout of Time Records to access the Time Clock')
            return redirect(url_for('records.main'))
    user_count = Users.query.count()
    if user_count == 0:
        return redirect(url_for('setup.show'))
    return render_template("clock.html")

@clock.route('/showmain')
def showmain():
    if current_user.is_authenticated:
        return redirect(url_for('clock.punches'))
    else:
        return redirect(url_for('clock.loginshow'))

@clock.route('/login/show')
def loginshow():
    form = PunchForm()
    form.name.choices = getUsers()
    form.process()
    return render_template('clock-login.html',
                           form=form)

@clock.post('/login')
def login():
    form = PunchForm()
    user = form.name.data
    password = form.password.data
    
    if user == '':
        return '', 404

    check_user = Users.query.filter_by(id=user).first_or_404()
    if not check_password_hash(check_user.pass_hash, password):
        flash('Password Incorrect')
        form.name.choices = getUsers()
        form.name.default = user
        form.process()
        return render_template('clock-login.html',
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
    now = datetime.now()
    time_now = datetime.strptime(now.strftime("%H:%M:%S"), "%H:%M:%S").time()
    
    type = request.args.get('type', default='', type=str)
    edit_user = Users.query.get(current_user.id)
    if type == 'i' and current_user.last_clock: #punch in already punched in
        # flag current punch for review
        # add new punch and update user
        # print("in -> in")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.flag = 'y'
        new_punch = Punch(clock_date=date.today(), clock_in=time_now,
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash('Clocked In')
        
    if type == 'i' and not current_user.last_clock: ### punch in not punched in
        # add new punch and update user
        # print("out -> in")
        new_punch = Punch(clock_date=date.today(), clock_in=time_now, 
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash('Clocked In')

    if type == 'o' and not current_user.last_clock: # punch out not punched in
        # add new punch out and clear user punch and flag for review
        # print("out -> out")
        new_punch = Punch(clock_date=date.today(), clock_out=time_now, 
                          flag='y', user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        flash('Clocked Out')

    if type == 'o' and current_user.last_clock: ### punch out and punched in
        # edit punch and clear user punch
        # print("in -> out")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.clock_out = time_now
        edit_user.last_clock = None
        time_total = getTimeTotal(edit_punch.clock_in, edit_punch.clock_out)
        edit_punch.time_total = time_total
        edit_punch.flag = 'n' if time_total else 'y'
        db.session.commit()
        flash('Clocked Out')
    
    return redirect(url_for('clock.punches'))

@clock.route('/punches')
@login_required
def punches():
    last:int = 20
    punches = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_date), desc(Punch.clock_in),desc(Punch.clock_out)).limit(last)
    return render_template('punches.html',
                           punches=punches,
                           last=last)

@clock.route('/punch/flag')
@login_required
def punchflag():
    id = request.args.get('id', default='', type=int)
    flag = request.args.get('flag', default='flag', type=str)
    punch = Punch.query.get_or_404(id)
    punch.flag = 'n' if flag == 'unflag' else 'y'
    db.session.commit()
    return render_template('punch-row.html',
                           punch=punch)

@clock.post('/profile/show')
@login_required
def profileshow():
    return render_template('clock-profile.html')

@clock.post('/profile/editshow')
@login_required
def profileeditshow():
    form = UserProfile()
    form.name.default = current_user.name
    form.email.default = current_user.email
    form.process()
    return render_template('clock-profile-edit.html',
                           form=form)

@clock.post('/profile/edit')
@login_required
def profileedit():
    user = Users.query.get(current_user.id)
    form = UserProfile()
    user.name = form.name.data
    user.email = form.email.data
    db.session.commit()
    return render_template('clock-profile.html')

@clock.post('/profile/pwshow')
@login_required
def profilepwshow():
    form = UserPW()
    return render_template('clock-profile-pw.html',
                           form=form)

@clock.post('/profile/pwedit')
@login_required
def profilepwedit():
    user = Users.query.get(current_user.id)
    form = UserPW()
    if not check_password_hash(current_user.pass_hash, form.admin_pass.data):
        message = "current password incorrect"
        return render_template('clock-profile-pw.html',
                               form=form,
                               message=message)
    
    if form.password1.data != form.password2.data:
        message = "passwords do not match"
        return render_template('clock-profile-pw.html',
                               form=form,
                               message=message)
    
    pass_hash = generate_password_hash(form.password1.data)
    user.pass_hash = pass_hash
    db.session.commit()
    return render_template('clock-profile.html')

@clock.route('/date')
def getdate():
    getdate = date.today()
    return render_template('clock-date.html',
                           getdate=getdate)