from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship

from . import db, max_vars

class Punch(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    clock_date  = db.Column(db.Date)
    clock_in    = db.Column(db.Time)
    clock_out   = db.Column(db.Time)
    time_total  = db.Column(db.Time)
    flag        = db.Column(db.String(1), default='n') # flag for admin review
    user        = relationship("Users", primaryjoin='Punch.user_id==Users.id')
    flag_note   = db.Column(db.String(max_vars.MAX_PUNCH_NOTE))
   
class Users(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(max_vars.MAX_NAME))
    employee_id = db.Column(db.String(max_vars.MAX_EMPLOYEE))
    email       = db.Column(db.String(max_vars.MAX_EMAIL))
    pass_hash   = db.Column(db.String(max_vars.MAX_PASS_HASH))
    active      = db.Column(db.String(1), default='y')
    admin       = db.Column(db.String(1), default='n')
    date_added  = db.Column(db.DateTime, default=datetime.now)
    last_login  = db.Column(db.DateTime)
    pw_last     = db.Column(db.DateTime)
    pw_change   = db.Column(db.String(1), default='n')
    last_clock  = db.Column(db.Integer, db.ForeignKey('punch.id'))
    time_format = db.Column(db.Integer, default=0)
    last_punch  = db.Column(db.Integer, default=20)
