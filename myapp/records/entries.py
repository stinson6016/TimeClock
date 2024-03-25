from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MO

from .webforms import SearchPunches, EditPunch, NewPunch
from .extra import searchPunchData
from .. import db
from ..extra import getUsers, getTimeTotal
from ..models import Users, Punch

entries = Blueprint("entries", __name__,
                    template_folder='templates')

@entries.route('/')
@login_required
def showportal():
    first_day_search = (datetime.now() - relativedelta(weekday=MO(-1))) # get last Friday.strftime(dateformat)
    last_day_search = (first_day_search + timedelta(weeks = 1)) - timedelta(days = 1)
    form = SearchPunches()
    form.employee.choices = getUsers(all='y')
    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.process()
    
    punches, flag_count = searchPunchData(first_day_search, last_day_search)
    return render_template('punches/punches-table.html',
                           form = form,
                           punches=punches,
                           flag_count=flag_count)

@entries.post('/search')
@login_required
def portalsearch():
    quick = request.args.get('quick', default='', type=str)
    form = SearchPunches()
    form.employee.choices = getUsers(all='y')
    employee = form.employee.data if form.employee.data else None
    flag = form.flagged.data if form.flagged.data else None
    first, last = quickSearch(quick)
    if not quick:
        first_day_search = form.start_date.data if form.start_date.data else first
        last_day_search = form.end_date.data if form.end_date.data else last
    else: 
        first_day_search = first
        last_day_search = last
    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.process()
    punches, flag_count = searchPunchData(first_day_search, last_day_search, employee, flag)
    return render_template('punches/punches-table.html',
                           form = form,
                           punches=punches,
                           flag_count=flag_count)

@entries.post('/newshow')
@login_required
def portalnewshow():
    form = NewPunch()
    form.user_id.choices = getUsers()
    form.clock_date.default = date.today()
    form.process()
    return render_template('punches/punches-new.html',
                           form=form)

@entries.post('/new')
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
    return redirect(url_for('records.entries.portalshowrow', id=punch.id))

@entries.post('/editshow')
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
    return render_template('punches/punches-edit.html',
                           form=form,
                           punch=punch)

@entries.post('/edit')
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
    return redirect(url_for('records.entries.portalshowrow', id=punch.id))

@entries.delete('/delete')
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

@entries.route('/showrow', methods=['GET', 'POST'])
@login_required
def portalshowrow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    return render_template('punches/punches-row.html',
                           punch=punch)

@entries.post('/cancel')
@login_required
def portalcancel():
    return '', 200


def quickSearch(quick:str):
    import calendar
    today = datetime.now()
    if quick == '' or quick == 'tw':
        first = (today - relativedelta(weekday=MO(-1)))
        last = (first + timedelta(weeks = 1)) - timedelta(days = 1)
    elif quick=='lw':
        first = (today - relativedelta(weekday=MO(-2)))
        last =  (first + timedelta(weeks = 1)) - timedelta(days = 1)
    elif quick=='td':
        first = today
        last = today
    elif quick=='yd':
        first = today - timedelta(days = 1)
        last = today - timedelta(days = 1)
    elif quick=='tm':
        first = today.replace(day=1)
        mon_cal = calendar.monthrange(today.year, today.month)
        last = datetime.strptime(  str(today.year) +"-"+ str(today.month) +"-"+ str(mon_cal[1]) , "%Y-%m-%d")
    elif quick=='lm':
        first = (today - timedelta(days=today.day)).replace(day=1)
        mon_cal = calendar.monthrange(first.year, first.month)
        last = datetime.strptime(  str(first.year) +"-"+ str(first.month) +"-"+ str(mon_cal[1]) , "%Y-%m-%d")
        print(first)
        print(last)
    elif quick=='ty':
        first = today.date().replace(month=1, day=1)
        last = today.date().replace(month=12, day=31)
        return first, last
    elif quick=='ly':
        first = today.date().replace(month=1, day=1) - relativedelta(years=1)
        last = today.date().replace(month=12, day=31) - relativedelta(years=1)
        return first, last

    first_date = first.date()
    last_date = last.date()
    return first_date, last_date