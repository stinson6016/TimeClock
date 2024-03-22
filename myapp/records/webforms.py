from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, TimeField, DateTimeField
from wtforms.validators import DataRequired, EqualTo, Length

class RecordsLogin(FlaskForm):
    name        = SelectField   ('Admin', validators=[DataRequired()])
    password    = PasswordField ("Password", validators=[DataRequired(), Length(max=100)])
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
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired()])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."})
    password1   = PasswordField ('Password', validators=[DataRequired(), Length(min=4)])
    password2   = PasswordField ('Password2', validators=[DataRequired(), Length(min=4)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin      = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserNew(FlaskForm):
    name        = StringField   ('name', render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired()])
    email       = EmailField    ('email', render_kw={"placeholder": " (Email - Optional) ..."})
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New password) ..."}, validators=[DataRequired(), Length(min=4)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm password) ..."}, validators=[DataRequired(), Length(min=4)])
    active      = SelectField   ('active', choices=[('y','Active'),('n', 'Disabled')])
    change      = SelectField   ('active', choices=[('n',''),('y', 'Change Password next logon')])
    admin      = SelectField   ('active', choices=[('n','Employee'),('y', 'Admin')])

class UserPW(FlaskForm):
    admin_pass  = PasswordField ('Admin Password', render_kw={"placeholder": " (Your password) ..."}, validators=[DataRequired()])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New Password) ..."}, validators=[DataRequired(), Length(min=4)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm Password) ..."}, validators=[DataRequired(), Length(min=4)])
    submit      = SubmitField   ('Save')