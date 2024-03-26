from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship

from . import db
from .maxvars import *

class Punch(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    type        = db.Column(db.String(1), default='n') # normal ? holiday ? make up ? # not used
    clock_date  = db.Column(db.Date)
    clock_in    = db.Column(db.Time)
    clock_out   = db.Column(db.Time)
    time_total  = db.Column(db.Time)
    flag        = db.Column(db.String(1), default='n') # flag for admin review
    user        = relationship("Users", primaryjoin='Punch.user_id==Users.id')

class Settings(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    comp_name    = db.Column(db.String(MAX_SET_COMP_NAME))
    email_active = db.Column(db.String(1))
    email_server = db.Column(db.String(MAX_SET_EMAIL_SERVER))
    email_send   = db.Column(db.String(MAX_SET_EMAIL_SEND))
    email_user   = db.Column(db.String(MAX_SET_EMAIL_USER))
    email_pass   = db.Column(db.String(MAX_SET_EMAIL_PASS))
    email_port   = db.Column(db.String(MAX_SET_EMAIL_PORT))
    email_secure = db.Column(db.String(1))
    
class Users(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(MAX_NAME))
    employee_id = db.Column(db.String(MAX_EMPLOYEE))
    email       = db.Column(db.String(MAX_EMAIL))
    pass_hash   = db.Column(db.String(MAX_PASS_HASH))
    active      = db.Column(db.String(1), default='y')
    admin       = db.Column(db.String(1), default='n')
    date_added  = db.Column(db.DateTime, default=datetime.now)
    last_login  = db.Column(db.DateTime)
    pw_last     = db.Column(db.DateTime)
    pw_change   = db.Column(db.String(1), default='n')
    last_clock  = db.Column(db.Integer, db.ForeignKey('punch.id'))
