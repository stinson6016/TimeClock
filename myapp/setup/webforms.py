from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from .. import max_vars

class SetupForm(FlaskForm):
    comp_name    = StringField   ("Company's Name", validators=[DataRequired(), Length(max=max_vars.MAX_SET_COMP_NAME)])
    name        = StringField   ("First Admin's Name", render_kw={"placeholder": " (Name) ..."}, validators=[DataRequired(), Length(max=max_vars.MAX_NAME)])
    email       = EmailField    ("Admin's Email", render_kw={"placeholder": " (Email - Optional) ..."}, validators=[Length(max=max_vars.MAX_EMAIL)])
    password1   = PasswordField ('Password', render_kw={"placeholder": " (New Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Confirm Password', render_kw={"placeholder": " (Confirm Password) ..."}, validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit      = SubmitField   ('Save')