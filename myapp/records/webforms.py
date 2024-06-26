from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, TimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length

from .. import max_vars

class RecordsLogin(FlaskForm):
    name        = SelectField   ('Admin', validators=[DataRequired()])
    password    = PasswordField ("Password", validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
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
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=max_vars.MAX_NAME)])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=max_vars.MAX_EMAIL)])
    password1   = PasswordField ('Password', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Password2', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin       = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserNew(FlaskForm):
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=max_vars.MAX_NAME)])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=max_vars.MAX_EMAIL)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin       = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserPW(FlaskForm):
    admin_pass  = PasswordField ('Admin Password', render_kw={"placeholder": " (Your password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit      = SubmitField   ('Save')

class CompanyEdit(FlaskForm):
    comp_name    = StringField   ("Name", validators=[DataRequired(), Length(max=max_vars.MAX_SET_COMP_NAME)])
    email_active = BooleanField  ('Email Active')
    email_server = StringField   ("Email Server", validators=[Length(max=max_vars.MAX_SET_EMAIL_SERVER)])
    email_send   = EmailField    ("send as", validators=[Length(max=max_vars.MAX_SET_EMAIL_SEND)])
    email_user   = StringField   ("Email User", validators=[Length(max=max_vars.MAX_SET_EMAIL_USER)])
    email_pass   = PasswordField ("password", validators=[Length(max=max_vars.MAX_SET_EMAIL_PASS)])
    email_port   = IntegerField  ("port", validators=[Length(max=max_vars.MAX_SET_EMAIL_PORT)])
    email_secure = SelectField   ("secure", choices=[("0","none"),("1","TLS")])
    submit       = SubmitField   ('Save')

# enter email to get a password reset link
class LostPassword(FlaskForm):
	email       = EmailField	("Enter your Email to reset your password", validators=[DataRequired(), Length(max=max_vars.MAX_EMAIL)])
	submit      = SubmitField   ("Submit")

class PasswordSet(FlaskForm):
    password1   = PasswordField ('New password', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Confirm new password', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit 		= SubmitField	("Save")