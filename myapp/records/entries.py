from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import datetime

from .extra import search_punch_data, quick_search, search_flagged
from .webforms import SearchPunches, EditPunch, NewPunch
from .. import db
from ..extra import get_users, get_time_total
from ..models import Users, Punch

entries = Blueprint("entries", __name__,
                    template_folder='templates')

@entries.route('/')
@login_required
def showportal():
    # quick load default page while pulling data
    first_day_search = date.today()
    last_day_search = date.today()
    form = SearchPunches()
    form.employee.choices = [(('', 'All Employees'))]
    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.process()
    
    return render_template('punches/punches.html',
                           form = form,
                           page='t')

@entries.post('/search')
@login_required
def portalsearch():
    quick = request.args.get('quick', default='', type=str)
    get_flag = request.args.get('flag', default=None, type=str)
    get_employee = request.args.get('employee', default=None, type=str)
    form = SearchPunches()
    
    employee = form.employee.data if form.employee.data else get_employee
    flag = form.flagged.data if form.flagged.data else get_flag
    first, last = quick_search(quick)
    if not quick:
        first_day_search = form.start_date.data if form.start_date.data else first
        last_day_search = form.end_date.data if form.end_date.data else last
    else: 
        first_day_search = first
        last_day_search = last
    
    form.employee.choices = get_users(all='y')
    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.flagged.default = flag
    form.employee.default = employee
    form.process()
    punches_master = search_punch_data(first_day_search, last_day_search, employee, flag)
    punches = db.paginate(punches_master, page=1, per_page=20, error_out=False)
    page_search = punches.next_num
    return render_template('punches/punches-table.html',
                           form = form,
                           punches=punches,
                           start=first_day_search,
                           end=last_day_search,
                           page='t',
                           employee=employee,
                           flag=flag,
                           page_search=page_search)

@entries.post('/search/showmore')
@login_required
def searchshowmore():
    flag = request.args.get('flag', default=None, type=str)
    employee = request.args.get('employee', default=None, type=str)
    start = request.args.get('start', default='', type=str)
    end = request.args.get('end', default='', type=str)
    page_search = request.args.get('page_search', default='', type=int)
    punches_master = search_punch_data(start, end, employee, flag)
    punches = db.paginate(punches_master, page=page_search, per_page=20, error_out=False)
    page_search = punches.next_num
    return render_template('punches/punches-row-build.html',
                           punches=punches,
                           start=start,
                           end=end,
                           page='t',
                           employee=employee,
                           flag=flag,
                           page_search=page_search)


@entries.post('/getflagged')
@login_required
def getflagged():
    start = request.args.get('start', default='', type=str)
    end = request.args.get('end', default='', type=str)
    employee = request.args.get('employee', default=None)
    flag_count = search_flagged(start, end, employee)
    return render_template('punches/punches-flagged.html',
                           flag_count=flag_count,
                           start=start,
                           end=end,
                           employee=employee)

@entries.post('/newshow')
@login_required
def portalnewshow():
    form = NewPunch()
    form.user_id.choices = get_users()
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
        time_total = get_time_total(start_time, end_time)
    else:
        time_total = None
    punch = Punch(clock_date=form.clock_date.data, user_id=form.user_id.data,
                  clock_in=start_time, clock_out=end_time,
                  time_total=time_total, flag=form.flag.data)
    db.session.add(punch)
    # set user punched in if only adding a clock in and date is today
    if start_time and not end_time and form.clock_date.data == date.today():
        user = Users.query.get(form.user_id.data)
        user.last_clock = punch.id
    db.session.commit()
    return redirect(url_for('records.entries.portalshowrow', id=punch.id))

@entries.post('/editshow')
@login_required
def portaleditshow():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    form = EditPunch()
    form.user_id.choices = get_users()
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
        punch.time_total = get_time_total(punch.clock_in, punch.clock_out)
        user = Users.query.get(form.user_id.data)
        if user.last_clock == punch.id:
            user.last_clock = None
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

@entries.post('/shownote')
@login_required
def portalshownote():
    id = request.args.get('id', default='', type=int)
    punch = Punch.query.get_or_404(id)
    return render_template('punches/punches-row-note.html',
                           punch=punch)

@entries.route('/showkey')
@login_required
def showkey():
    return render_template('punches/punches-key.html')

@entries.route('/hidekey')
@login_required
def hidekey():
    return render_template('punches/punches-key-min.html')