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
# @hours.route('/show')
# @login_required
# def show():
#     first_day_search = (datetime.now() - relativedelta(weekday=MO(-1)))
#     last_day_search = (first_day_search + timedelta(weeks = 1)) - timedelta(days = 1)
#     form = SearchPunches()
#     form.employee.choices = getUsers(all='y')
#     form.start_date.default = first_day_search
#     form.end_date.default = last_day_search
#     form.process()
#     user_hours = {}
#     pull_users = Punch.query.join(Punch.user).where(Punch.clock_date >= first_day_search, Punch.clock_date <= last_day_search).group_by(Users.name)
#     for user in pull_users:
#         user_hours[user.user_id] = getHours(user.user_id, first_day_search, last_day_search)

#     return render_template('hours/hours.html',
#                            form=form,
#                            user_hours=user_hours,
#                            pull_users=pull_users)

@hours.route('/search', methods=['GET', 'POST'])
@login_required
def portalsearch():
    
    form = SearchPunches()
    form.employee.choices = getUsers(all='y')
    employee = form.employee.data if form.employee.data else None
    first_day_search = form.start_date.data if form.start_date.data else (datetime.now() - relativedelta(weekday=MO(-1)))
    last_day_search = form.end_date.data if form.end_date.data else (first_day_search + timedelta(weeks = 1)) - timedelta(days = 1)

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