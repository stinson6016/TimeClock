from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, TimeField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length

from ..maxvars import *

class RecordsLogin(FlaskForm):
    name        = SelectField   ('Admin', validators=[DataRequired()])
    password    = PasswordField ("Password", validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    submit      = SubmitField   ("Login")

class SearchPunches(FlaskForm):
    employee    = SelectField   ("Employee")
    start_date  = DateField     ("Start Date")
    end_date    = DateField     ("End Date")
    flagged     = SelectField   ('Flagged', choices=[('',''),('y', 'Yes')])
    submit      = SubmitField   ("Search")

class EditPunch(FlaskForm):
    user_id     = SelectField   ("Employee")
    clock_date  = DateField     ("clock date")
    clock_in    = TimeField     ("Start Time", format='%H:%M:%S', render_kw={"step": "1"})
    clock_out   = TimeField     ("End Time", format='%H:%M:%S', render_kw={"step": "1"})
    flag        = SelectField   ('Flagged', choices=[('n','No'),('y', 'Yes')])

class NewPunch(FlaskForm):
    user_id     = SelectField   ("Employee", validators=[DataRequired()])
    clock_date  = DateField     ("clock date", validators=[DataRequired()])
    clock_in    = TimeField     ("Start Time")
    clock_out   = TimeField     ("End Time")
    flag        = SelectField   ('Flagged', choices=[('n','No'),('y', 'Yes')])

class UserEdit(FlaskForm):
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=MAX_NAME)])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=MAX_EMAIL)])
    password1   = PasswordField ('Password', validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    password2   = PasswordField ('Password2', validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin       = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserNew(FlaskForm):
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=MAX_NAME)])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=MAX_EMAIL)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New password) ..."}, validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm password) ..."}, validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin       = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserPW(FlaskForm):
    admin_pass  = PasswordField ('Admin Password', render_kw={"placeholder": " (Your password) ..."}, validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New Password) ..."}, validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm Password) ..."}, validators=[DataRequired(), Length(min=MIN_PASS_STR, max=MAX_PASS_STR)])
    submit      = SubmitField   ('Save')

class CompanyEdit(FlaskForm):
    comp_name    = StringField   ("Name", validators=[DataRequired(), Length(max=MAX_SET_VALUE)])
    email_active = BooleanField  ('Email Active')
    email_server = StringField   ("Email Server", validators=[Length(max=MAX_SET_VALUE)])
    email_send   = EmailField    ("send as", validators=[Length(max=MAX_SET_VALUE)])
    email_user   = StringField   ("Email User", validators=[Length(max=MAX_SET_VALUE)])
    email_pass   = PasswordField ("password", validators=[Length(max=MAX_SET_VALUE)])
    email_port   = IntegerField  ("port")
    email_secure = SelectField   ("secure", choices=[("0","none"),("1","TLS"),("2","SSL")])
    submit       = SubmitField   ('Save')

