from datetime import date, datetime
from flask import Blueprint, render_template, request
from flask_login import login_required

from .extra import quick_search, search_flagged
from .webforms import SearchPunches

from ..extra import get_users
from ..models import Punch, Users

hours = Blueprint('hours', __name__,
                  template_folder='templates')

@hours.post('/show')
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
@hours.post('/search')
@login_required
def portalsearch():
    quick = request.args.get('quick', default='', type=str)
    get_employee = request.args.get('employee', default=None, type=str)
    form = SearchPunches()
    
    employee = form.employee.data if form.employee.data else get_employee

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
    form.employee.default = employee
    form.process()
    user_hours:dict[int, str] = {}
    user_flagged:dict[int, bool] = {}
    if employee:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee).group_by(Users.name)
    else:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search).group_by(Users.name)
    for user in pull_users:
        user_hours[user.user_id], user_flagged[user.user_id] = get_hours(user.user_id, first_day_search, last_day_search)
    return render_template('hours/hours-search.html',
                           form = form,
                           user_hours=user_hours,
                           user_flagged=user_flagged,
                           pull_users=pull_users,
                           page='h',
                           employee=employee,
                           start=first_day_search,
                           end=last_day_search)

@hours.post('/print')
@login_required
def printhours():
    employee = request.args.get('employee', default="", type=str) 
    first_day_search = request.args.get('start', default="", type=str)
    last_day_search = request.args.get('end', default="", type=str) 
    
    user_hours:dict[int, str] = {}
    user_flagged:dict[int, bool] = {}

    if employee:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee).group_by(Users.name)
    else:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search).group_by(Users.name)
    
    for user in pull_users:
        user_hours[user.user_id], user_flagged[user.user_id] = get_hours(user.user_id, first_day_search, last_day_search)
    start:str = (datetime.strptime(first_day_search, '%Y-%m-%d').date()).strftime("%m/%d/%Y")
    end:str = (datetime.strptime(last_day_search, '%Y-%m-%d').date()).strftime("%m/%d/%Y")
    return render_template('hours/print-hours.html',
                           user_hours=user_hours,
                           user_flagged=user_flagged,
                           pull_users=pull_users,
                           employee=employee,
                           start=start,
                           end=end)

@hours.post('/getflagged')
@login_required
def getflagged():
    start = request.args.get('start', default='')
    end = request.args.get('end', default='')
    employee = request.args.get('employee', default=None)
    flag_count = search_flagged(start, end, employee)
    return render_template('punches/punches-flagged.html',
                           flag_count=flag_count,
                           start=start,
                           end=end,
                           employee=employee)

def get_hours(user_id: int, first_day_search: date, last_day_search: date) -> tuple[str, bool]:
    punches = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==user_id)
    total_hour: int = 0
    total_minute:int = 0
    total_second:int = 0
    flagged: bool = False
    for punch in punches:
        flagged = True if punch.flag == 'y' else flagged
        
        if punch.time_total:
            hour, minute, second = punch.time_total.strftime("%H:%M:%S").split(":")
            hour, minute, second = int(hour), int(minute), int(second)
            total_hour = hour + total_hour
            total_minute = minute + total_minute
            total_second = second + total_second

    sec_div: int = total_second // 60
    seconds: str = str(total_second % 60)
    min_div: int = (total_minute + sec_div) // 60
    minutes: str = str((total_minute + sec_div) % 60)
    hours: str = str(total_hour + min_div)
    total_hours = (f"{hours}:{minutes:02}:{seconds:02}")
    return total_hours, flagged
