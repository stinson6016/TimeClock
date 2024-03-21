from flask_login import UserMixin
# from sqlalchemy.orm import relationship
from datetime import datetime

from . import db

class Punch(db.Model):
    id          = db.Column(db.String(36), primary_key=True)
    user_id     = db.Column(db.String(36), db.ForeignKey('users.id'))
    type        = db.Column(db.String(1), default='n') # normal ? holiday ? make up ?
    clock_in    = db.Column(db.DateTime)
    clock_out   = db.Column(db.DateTime)
    flag        = db.Column(db.String(1), default='n') # flag for admin review


class Users(db.Model, UserMixin):
    id          = db.Column(db.String(36), primary_key=True)
    name        = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    email       = db.Column(db.String(100))
    pass_hash   = db.Column(db.String(200))
    active      = db.Column(db.String(1), default='y')
    admin       = db.Column(db.String(1), default='n')
    date_added  = db.Column(db.DateTime, default=datetime.now)
    last_login  = db.Column(db.DateTime)
    pw_last     = db.Column(db.DateTime)
    pw_change   = db.Column(db.String(1), default='n')
    last_clock  = db.Column(db.String(36), db.ForeignKey('punch.id'))

