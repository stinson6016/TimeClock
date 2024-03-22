from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta

from .webforms import RecordsLogin, SearchPunches, EditPunch, NewPunch
from .. import db
from ..extra import getUsersAdmins, getUsers, getTimeTotal
from ..models import Users, Punch

records = Blueprint("records", __name__,
                    template_folder='templates')

@records.route('/')
def main():
    if current_user.is_authenticated:
        if current_user.admin != 'y':
            return redirect(url_for('clock.home'))
    return render_template("records.html")

@records.route('/showmain')
def showmain():
    if current_user.is_authenticated:
        return redirect(url_for('records.portal'))
    else: 
        return redirect(url_for('records.loginshow'))
        

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
    return redirect(url_for('records.portal'))

@records.route('/portal')
@login_required
def portal():
    form = SearchPunches()
    form.employee.choices = getUsers()
    form.start_date.default = date.today()
    form.end_date.default = date.today()
    form.process()
    
    punches, flag_count = searchPunchData()
    return render_template('portal.html',
                           form = form,
                           punches=punches,
                           flag_count=flag_count)

@records.post('/portal/search')
@login_required
def portalsearch():
    form = SearchPunches()
    form.employee.choices = getUsers()
    employee = form.employee.data if form.employee.data else None
    flag = form.flagged.data if form.flagged.data else None

    punches, flag_count = searchPunchData(form.start_date.data, form.end_date.data, employee, flag)
    return render_template('portal.html',
                           form = form,
                           punches=punches,
                           flag_count=flag_count)

@records.post('/portal/newshow')
@login_required
def portalnewshow():
    form = NewPunch()
    form.user_id.choices = getUsers()
    form.clock_date.default = date.today()
    form.process()
    return render_template('punches-new.html',
                           form=form)

@records.post('/portal/new')
@login_required
def portalnew():
    form = NewPunch()
    start_time = form.clock_in.data if form.clock_in.data else None
    end_time = form.clock_out.data if form.clock_out.data else None
    if start_time and end_time:
        time_total = getTimeTotal(start_time, end_time)
    else:
        time_total = None
    punch = Punch(clock_date=form.clock_date.data, user_id=form.user_id.data,
                  clock_in=start_time, clock_out=end_time,
                  time_total=time_total, flag=form.flag.data)
    db.session.add(punch)
    db.session.commit()
    return redirect(url_for('records.portalshowrow', id=punch.id))

@records.post('/portal/editshow')
@login_required
def portaleditshow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = EditPunch()
    form.user_id.choices = getUsers()
    form.user_id.default = punch.user_id
    form.clock_date.default = punch.clock_date
    form.clock_in.default = punch.clock_in
    form.clock_out.default = punch.clock_out
    form.flag.default = punch.flag
    form.process()
    return render_template('punches-edit.html',
                           form=form,
                           punch=punch)

@records.post('/portal/edit')
@login_required
def portaledit():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = EditPunch()
    punch.user_id = form.user_id.data
    punch.clock_date = form.clock_date.data
    punch.clock_in = form.clock_in.data if form.clock_in.data else None
    punch.clock_out = form.clock_out.data if form.clock_out.data else None
    punch.flag = form.flag.data
    if form.clock_in.data and form.clock_out.data:
        punch.time_total = getTimeTotal(punch.clock_in, punch.clock_out)
    db.session.commit()
    return redirect(url_for('records.portalshowrow', id=punch.id))

@records.delete('/portal/delete')
@login_required
def portaldelete():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    check_user = Users.query.where(Users.last_clock==punch.id).first()
    if check_user:
        check_user.last_clock = None
        # db.session.commit()
    db.session.delete(punch)
    db.session.commit()
    return '', 200

@records.route('/portal/showrow', methods=['GET', 'POST'])
@login_required
def portalshowrow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    return render_template('punches-row.html',
                           punch=punch)

@records.post('/portal/cancel')
@login_required
def portalcancel():
    return '', 200

@records.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('records.loginshow'))


def searchPunchData(start_date:date = date.today(), end_date:date = date.today(), user_id:int = None, flag:str = None):
    # end_date = end_date + timedelta(days= 1)
    
    if not user_id and not flag:
        punches = Punch.query.where(Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(Punch.clock_date,Punch.clock_in)
        flag_count = Punch.query.where(Punch.flag=='y', Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    elif not user_id and flag:
        punches = Punch.query.where(Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(Punch.clock_date,Punch.clock_in)
        flag_count = Punch.query.where(Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    elif user_id and not flag:
        punches = Punch.query.where(Punch.user_id==user_id, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(Punch.clock_date,Punch.clock_in)
        flag_count = Punch.query.where(Punch.flag=='y', Punch.user_id==user_id, Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    elif user_id and flag:
        punches = Punch.query.where(Punch.user_id==user_id, Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(Punch.clock_date,Punch.clock_in)
        flag_count = Punch.query.where(Punch.user_id==user_id, Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    print(flag_count)
    return punches, flag_count