from datetime import date
from flask import Blueprint, render_template, request
from flask_login import login_required

from .extra import quickSearch, searchFlagged
from .webforms import SearchPunches

from ..extra import getUsers
from ..models import Punch, Users

hours = Blueprint('hours', __name__,
                  template_folder='templates')

@hours.route('/show')
@login_required
def show():
    # quick load default page while pulling data
    form = SearchPunches()
    form.start_date.default = date.today()
    form.end_date.default = date.today()
    form.employee.choices = [(('', 'All Employees'))]
    form.process()
    return render_template('hours/hours.html',
                           form=form,
                           page='h')
@hours.route('/search', methods=['GET', 'POST'])
@login_required
def portalsearch():
    quick = request.args.get('quick', default='', type=str)
    get_employee = request.args.get('employee', default=None, type=str)
    form = SearchPunches()
    
    employee = form.employee.data if form.employee.data else get_employee

    first, last = quickSearch(quick)
    if not quick:
        first_day_search = form.start_date.data if form.start_date.data else first
        last_day_search = form.end_date.data if form.end_date.data else last
    else: 
        first_day_search = first
        last_day_search = last
    
    form.employee.choices = getUsers(all='y')
    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.employee.default = employee
    form.process()
    user_hours = {}
    if employee:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee).group_by(Users.name)
        # flagged = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee, Punch.flag=='y').count()
    else:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search).group_by(Users.name)
        # flagged = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.flag=='y').count()
    for user in pull_users:
        user_hours[user.user_id] = getHours(user.user_id, first_day_search, last_day_search)
    return render_template('hours/hours-search.html',
                           form = form,
                           user_hours=user_hours,
                           pull_users=pull_users,
                        #    flagged=flagged,
                           page='h',
                           employee=employee,
                           start=first_day_search,
                           end=last_day_search)

@hours.post('/getflagged')
@login_required
def getflagged():
    start = request.args.get('start', default='')
    end = request.args.get('end', default='')
    employee = request.args.get('employee', default=None)
    flag_count = searchFlagged(start, end, employee)
    return render_template('punches/punches-flagged.html',
                           flag_count=flag_count,
                           start=start,
                           end=end,
                           employee=employee)

def getHours(user_id, first_day_search, last_day_search):
    punches = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==user_id)
    total_hour: int = 0
    total_minute:int = 0
    total_second:int = 0
    for punch in punches:
        test_punch = punch.time_total
        
        if test_punch:
            hour, minute, second = test_punch.strftime("%H:%M:%S").split(":")
            hour, minute, second = int(hour), int(minute), int(second)
            total_hour = hour + total_hour
            total_minute = minute + total_minute
            total_second = second + total_second

    sec_div = total_second // 60
    seconds = total_second % 60
    min_div = (total_minute + sec_div) // 60
    minutes = (total_minute + sec_div) % 60
    hours = total_hour + min_div
    total_hours = (f"{hours}:{minutes:02}:{seconds:02}")
    return total_hours
