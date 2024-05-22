from datetime import datetime, datetime, date, time
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from .. import db, max_vars
from ..extra import get_users, get_time_total
from ..models import Users, Punch
from .webforms import PunchForm, UserProfile, UserPW, FlagNote

clock = Blueprint("clock", __name__,
                  template_folder='templates')

@clock.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.admin == 'y':
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
        return redirect(url_for('clock.punches'), code=307)
    else:
        return redirect(url_for('clock.loginshow'), code=307)

@clock.post('/login/show')
def loginshow():
    form = PunchForm()
    form.name.choices = get_users()
    form.process()
    return render_template('clock-login.html',
                           form=form)

@clock.post('/login')
def login():
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
        return render_template('clock-login.html',
                               form=form)
    
    if check_user.pw_change == 'y':
        logging.warning(f'must rest password {check_user.name}')
        message='Must reset password to login'
        return render_template('clock-login-pw.html',
                               form=pw_form,
                               editid=check_user.id,
                               message=message)
    
    login_user(check_user)
    logging.info(f'Employee - {current_user.name} logged in')
    return redirect(url_for('clock.punches'), code=307)

@clock.post('/login/pwreset')
def loginpwreset():
    id = request.args.get('id', default='', type=str)
    user = Users.query.get_or_404(id)
    form = UserPW()
    if not check_password_hash(user.pass_hash, form.admin_pass.data):
        logging.warning(f'password reset incorrect password {user.name}')
        message = 'current password incorrect'
        return render_template('clock-login-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    if form.password1.data != form.password2.data:
        message='passwords do not match'
        return render_template('clock-login-pw.html',
                               form=form,
                               editid=user.id,
                               message=message)
    user.pass_hash = generate_password_hash(form.password1.data)
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    login_user(user)
    return redirect(url_for('clock.punches'), code=307)

@clock.post('/logout')
def logout():
    logging.info(f'Employee - {current_user.name} logged out')
    logout_user()
    flash('logged out')
    return redirect(url_for('clock.loginshow'), code=307)

@clock.post('/punch')
@login_required
def onepunch():
    now:datetime = datetime.now()
    time_now:time = datetime.strptime(now.strftime("%H:%M:%S"), "%H:%M:%S").time()
    
    type = request.args.get('type', default='', type=str)
    edit_user = Users.query.get(current_user.id)
    if type == 'i' and current_user.last_clock: #punch in already punched in
        # flag current punch for review
        # add new punch and update user
        # ("in -> in")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.flag = 'y'
        edit_punch.flag_note = 'auto - clocked in while already marked as clocked in'
        new_punch = Punch(clock_date=date.today(), clock_in=time_now,
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash(f'Clocked In - {time_now.strftime("%H:%M:%S")}')
        logging.info(f'{current_user.name} clocked in')
        
    if type == 'i' and not current_user.last_clock: ### punch in not punched in
        # add new punch and update user
        # ("out -> in")
        new_punch = Punch(clock_date=date.today(), clock_in=time_now, 
                          user_id=current_user.id)
        db.session.add(new_punch)
        db.session.commit()
        edit_user.last_clock = new_punch.id
        db.session.commit()
        flash(f'Clocked In - {time_now.strftime("%H:%M:%S")}')
        logging.info(f'{current_user.name} clocked in, error already clocked in')

    if type == 'o' and not current_user.last_clock: # punch out not punched in
        # add new punch out and clear user punch and flag for review
        # ("out -> out")
        new_punch = Punch(clock_date=date.today(), clock_out=time_now, 
                          flag='y', user_id=current_user.id,
                          flag_note='auto - clocked out while already marked as clocked out')
        db.session.add(new_punch)
        db.session.commit()
        flash(f'Clocked Out - {time_now.strftime("%H:%M:%S")}')
        logging.info(f'{current_user.name} clocked out')

    if type == 'o' and current_user.last_clock: ### punch out and punched in
        # edit punch and clear user punch
        # ("in -> out")
        edit_punch = Punch.query.get(current_user.last_clock)
        edit_punch.clock_out = time_now
        edit_user.last_clock = None
        time_total = get_time_total(edit_punch.clock_in, edit_punch.clock_out)
        edit_punch.time_total = time_total
        edit_punch.flag = 'n' if time_total else 'y'
        db.session.commit()
        flash(f'Clocked Out - {time_now.strftime("%H:%M:%S")}')
        logging.info(f'{current_user.name} clocked out, error already clocked out')
    
    return redirect(url_for('clock.punches'), code=307)

@clock.post('/punches')
@login_required
def punches():
    return render_template('punches.html',
                           last=current_user.last_punch)

@clock.post('/pullpunches')
@login_required
def pullpunches():
    punches_master = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_date), desc(Punch.clock_in),desc(Punch.clock_out))
    punches = db.paginate(punches_master, page=1, per_page=current_user.last_punch, error_out=False)
    page_search = punches.next_num
    return render_template('punches-table.html',
                           punches=punches,
                           last=current_user.last_punch,
                           page_search=page_search)

@clock.post('pullpunches/showmore')
@login_required
def pullpunchesshowmore():
    page_search = request.args.get('page_search', default='', type=int)
    punches_master = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_date), desc(Punch.clock_in),desc(Punch.clock_out))
    punches = db.paginate(punches_master, page=page_search, per_page=current_user.last_punch, error_out=False)
    page_search = punches.next_num
    return render_template('punches-row-build.html',
                           punches=punches,
                           page_search=page_search)

@clock.post('/punch/flag')
@login_required
def punchflag():
    id = request.args.get('id', default='', type=int)
    flag = request.args.get('flag', default='flag', type=str)
    punch = Punch.query.get_or_404(id)
    punch.flag = 'n' if flag == 'unflag' else 'y'
    db.session.commit()
    return redirect(url_for('clock.punchshowrow',
                            id=punch.id), code=307)


@clock.post('/punch/noteshow')
@login_required
def punchnoteshow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = FlagNote()
    form.flag_note.default = punch.flag_note
    form.process()
    return render_template('punch-note.html',
                           form=form,
                           punch=punch)

@clock.post('/punch/note')
@login_required
def punchnote():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = FlagNote()
    punch.flag_note = form.flag_note.data
    db.session.commit()
    return redirect(url_for('clock.punchshowrow',
                            id=punch.id), code=307)

@clock.post('/punch/showrow')
@login_required
def punchshowrow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
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
    form.time_format.default = current_user.time_format
    form.last_punch.default = current_user.last_punch
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
    user.time_format = form.time_format.data
    user.last_punch = form.last_punch.data
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
    user.pw_last = datetime.today()
    user.pw_change = 'n'
    db.session.commit()
    return render_template('clock-profile.html')

@clock.post('/date')
def getdate():
    getdate = date.today()
    return render_template('clock-date.html',
                           getdate=getdate)

@clock.post('/showhelp')
@login_required
def showhelp():
    return render_template('punch-help.html')

@clock.post('/hidehelp')
@login_required
def hidehelp():
    return render_template('punch-help-min.html')