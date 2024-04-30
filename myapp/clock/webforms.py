from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Length

from .. import max_vars

class PunchForm(FlaskForm):
    name        = SelectField("Employee Name", validators=[DataRequired()])
    password    = PasswordField("Enter your password", validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit      = SubmitField("Login")

class UserPW(FlaskForm):
    admin_pass  = PasswordField ('Your Password', render_kw={"placeholder": " (Your password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Password2', render_kw={"placeholder": " (Confirm Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit      = SubmitField   ('Save')

class UserProfile(FlaskForm):
    name        = StringField   ("name", render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=max_vars.MAX_NAME)])
    email       = EmailField    ("email", render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=max_vars.MAX_EMAIL)])
    submit      = SubmitField   ('Save')

class FlagNote(FlaskForm):
    flag_note   = StringField   ("notes", render_kw={"placeholder": " (late punch) ..."}, validators=[Length(max=max_vars.MAX_PUNCH_NOTE)])