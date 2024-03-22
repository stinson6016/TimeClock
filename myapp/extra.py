from datetime import datetime, time, date

from .models import Users

def getUsers(all:str = 'n'):
    users = Users.query.where(Users.active == 'y', Users.admin == 'n').order_by(Users.name)
    start:str = 'All Employees' if all == 'y' else ''
    return_users = [("",start)]
    for user in users:
        return_users.append((user.id, user.name))
    return return_users

def getUsersAdmins():
    users = Users.query.where(Users.active == 'y', Users.admin == 'y').order_by(Users.name)
    return_users = [("","")]
    for user in users:
        return_users.append((user.id, user.name))
    return return_users

def getTimeTotal(start_time: time, end_time: time):
    
    # take time and convert to datetime because I'm lazy and this works
    start_datetime_str:str = str(date.today()) + " " + str(start_time)
    start_datetime:datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
    end_datetime_str:str = str(date.today()) + " " + str(end_time)
    end_datetime:datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

    sub_time = end_datetime - start_datetime
    return_time = datetime.strptime(str(sub_time), "%H:%M:%S").time()

    return return_time

PunchTypes = [
	('n', 'Normal'),
	('h', 'Holiday'),
	('m', 'Make Up')
	
]