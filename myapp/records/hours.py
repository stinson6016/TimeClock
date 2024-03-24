from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MO

from .webforms import SearchPunches
from .extra import searchPunchData

from .. import db
from ..extra import getUsers, converttime
from ..models import Punch, Users

hours = Blueprint('hours', __name__,
                  template_folder='templates')

@hours.route('/show')
@login_required
def show():
    form = SearchPunches()
    form.start_date.default = date.today()
    form.end_date.default = date.today()
    form.process()
    return render_template('hours/hours.html',
                           form=form)
@hours.route('/search', methods=['GET', 'POST'])
@login_required
def portalsearch():
    quick = request.args.get('quick', default='', type=str)
    form = SearchPunches()
    form.employee.choices = getUsers(all='y')
    employee = form.employee.data if form.employee.data else None

    first, last = quickSearch(quick)
    if not quick:
        first_day_search = form.start_date.data if form.start_date.data else first
        last_day_search = form.end_date.data if form.end_date.data else last
    else: 
        first_day_search = first
        last_day_search = last

    form.start_date.default = first_day_search
    form.end_date.default = last_day_search
    form.employee.default = employee
    form.process()
    # print(first_day_search)
    user_hours = {}
    if employee:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee).group_by(Users.name)
        flagged = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.user_id==employee, Punch.flag=='y').count()
    else:
        pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search).group_by(Users.name)
        flagged = Punch.query.where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search, Punch.flag=='y').count()
    for user in pull_users:
        user_hours[user.user_id] = getHours(user.user_id, first_day_search, last_day_search)
    return render_template('hours/hours-search.html',
                           form = form,
                           user_hours=user_hours,
                           pull_users=pull_users,
                           flagged=flagged)

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