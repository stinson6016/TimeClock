from datetime import date

from ..models import Punch


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