from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length

class PunchForm(FlaskForm):
    name   = SelectField("Employee Name", validators=[DataRequired(), Length(max=20)])
    password    = PasswordField("Enter your password", validators=[DataRequired()])
    submit      = SubmitField("Login")
