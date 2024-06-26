from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MO
from sqlalchemy import desc
import calendar
import logging

from ..models import Punch

def search_punch_data(start_date:date = date.today(), end_date:date = date.today(), user_id:int = None, flag:str = None):
    logging.debug(f'search user_id: {user_id}')
    if not user_id and not flag:
        logging.debug('search option 1')
        punches = Punch.query.where(Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(desc(Punch.clock_date),Punch.clock_in, Punch.clock_out)
    elif not user_id and flag:
        logging.debug('search option 2')
        punches = Punch.query.where(Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(desc(Punch.clock_date),Punch.clock_in, Punch.clock_out)
    elif user_id and not flag:
        logging.debug('search option 3')
        punches = Punch.query.where(Punch.user_id==user_id, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(desc(Punch.clock_date),Punch.clock_in, Punch.clock_out)
    elif user_id and flag:
        logging.debug('search option 4')
        punches = Punch.query.where(Punch.user_id==user_id, Punch.flag==flag, Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(desc(Punch.clock_date),Punch.clock_in, Punch.clock_out)
    else:
        logging.debug('search else')
        punches = Punch.query.where(Punch.clock_date >= start_date, Punch.clock_date <= end_date).order_by(desc(Punch.clock_date),Punch.clock_in, Punch.clock_out) 
    return punches

def search_flagged(start_date:date = date.today(), end_date:date = date.today(), user_id:int = None) -> int:
    if not user_id:
        flag_count = Punch.query.where(Punch.flag=='y', Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    else:
        flag_count = Punch.query.where(Punch.user_id==user_id, Punch.flag=='y', Punch.clock_date >= start_date, Punch.clock_date <= end_date).count()
    return flag_count

def quick_search(quick:str) -> tuple[date, date]:
    ''' returns the start and stop dates for doing a quick database search in a specific date range '''
    # bad code to get the start and finish dates for the searches
    today: datetime = datetime.now()
    logging.debug(f'search: {quick}')
    match quick:
        case 'tw' | '': # default / this week
            first: datetime = (today - relativedelta(weekday=MO(-1)))
            last: datetime = (first + timedelta(weeks = 1)) - timedelta(days = 1)
            logging.debug(f'first day: {first} last day: {last}')
        case 'lw': # last week
            first: datetime = (today - relativedelta(weekday=MO(-2)))
            last: datetime =  (first + timedelta(weeks = 1)) - timedelta(days = 1)
            logging.debug(f'first day: {first} last day: {last}')
        case 'td': # today
            first: datetime = today
            last: datetime = today
            logging.debug(f'first day: {first} last day: {last}')
        case 'yd': # yesterday 
            first: datetime = today - timedelta(days = 1)
            last: datetime = today - timedelta(days = 1)
            logging.debug(f'first day: {first} last day: {last}')
        case 'tm': # this month
            first: datetime = today.replace(day=1)
            mon_cal = calendar.monthrange(today.year, today.month)
            last: datetime = datetime.strptime(  str(today.year) +"-"+ str(today.month) +"-"+ str(mon_cal[1]) , "%Y-%m-%d")
            logging.debug(f'first day: {first} last day: {last}')
        case 'lm': # last month
            first: datetime = (today - timedelta(days=today.day)).replace(day=1)
            mon_cal = calendar.monthrange(first.year, first.month)
            last: datetime = datetime.strptime(  str(first.year) +"-"+ str(first.month) +"-"+ str(mon_cal[1]) , "%Y-%m-%d")
            logging.debug(f'first day: {first} last day: {last}')
        case 'ty': # this year
            first: date = today.date().replace(month=1, day=1)
            last: date = today.date().replace(month=12, day=31)
            logging.debug(f'first day: {first} last day: {last}')
            return first, last # don't have to convert to date
        case 'ly': # last year
            first: date = today.date().replace(month=1, day=1) - relativedelta(years=1)
            last: date = today.date().replace(month=12, day=31) - relativedelta(years=1)
            logging.debug(f'first day: {first} last day: {last}')
            return first, last # don't have to conver to date

    # convert the datetime to just date
    first_date: date = first.date()
    last_date: date = last.date()
    return first_date, last_date